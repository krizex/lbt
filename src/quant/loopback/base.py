#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from abc import abstractmethod, ABCMeta, abstractproperty
from contextlib import contextmanager
from datetime import datetime, timedelta, date
from multiprocessing import Pool

import signal
import tushare as ts

from quant.helpers import is_rising_trend
from quant.logger.logger import log
from quant.peak import Peak
from quant.loopback.result.base import Result
from quant.stock import Stock
import pickle as pickle
import matplotlib.pyplot as plt

from quant.utils import days_between

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def terminate_pool_and_exit(signum, frame):
    global g_pool
    log.warn('Handle signal')
    if g_pool is not None:
        log.info('Closing pool...')
        g_pool.terminate()
        g_pool.join()
    exit(1)


def setup_signal_handler(handler):
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, handler)


def build_stock(stock_info):
    (idx, (code, info)) = stock_info
    log.debug('%d Fetching %s %s', idx, code, info['name'])
    for _ in range(5):
        try:
            stock = Stock(code, info)
            return stock
        except Exception as e:
            log.error('Error fetching %s, retrying...', code)
            time.sleep(3)
    return None


def process_stock(stock):
    try:
        if len(stock.df) == 0:
            return stock

        stock.process()
    except:
        log.exception('Error occur when processing %s', stock.code)

    return stock


def loopback_stock(info):
    (loopback, stock) = info
    try:
        result = loopback.loopback_one(stock)
        stock.set_loopback_result(result)
    except Exception as e:
        log.exception('Error occur when looping back %s', stock.code)

    return stock


g_pool = None
@contextmanager
def create_pool(target):
    global g_pool
    if g_pool is None:
        setup_signal_handler(signal.SIG_IGN)
        log.debug('Create pool')
        g_pool = Pool(4)
        setup_signal_handler(terminate_pool_and_exit)

    log.debug('Enter pool: %s', target)
    start = datetime.now()
    yield g_pool
    cost = datetime.now() - start
    log.debug('Exit pool: %s, takes %d seconds', target, cost.total_seconds())


def avg(l):
    return sum(l) / 1.0 / len(l)


class LoopInterResult(object):
    def __init__(self):
        self.last_macd = 0.0
        self.last_ma_gap = 0.0


class Loopback(object, metaclass=ABCMeta):
    def __init__(self, persist_f, from_date, to_date):
        self.persist_f = self.persiste_f_name(persist_f)
        self.from_date = from_date
        self.to_date = to_date
        self.stocks = None

    def init(self):
        self.stocks = self.fetch_stocks()

    def persiste_f_name(self, name):
        if name:
            return name
        now = int(time.time())
        time_array = time.localtime(now)
        t = time.strftime("%Y-%m-%d", time_array)
        return 'data/stocks-%s.dat' % t

    def read_stocks_from_persist(self):
        log.info("Read stocks from file:%s", self.persist_f)
        with open(self.persist_f, 'rb') as f:
            return pickle.load(f)

    def persist_stocks(self, data):
        log.info("Persist stocks to file: %s", self.persist_f)
        os.makedirs(os.path.dirname(self.persist_f), exist_ok=True)
        with open(self.persist_f, 'wb') as f:
            pickle.dump(data, f)

    def fetch_stocks(self):
        if os.path.isfile(self.persist_f):
            stocks = self.read_stocks_from_persist()
        else:
            stocks = self._fetch_stocks()
            self.persist_stocks(stocks)

        log.info('Fetched all stocks')
        return self.process_stocks(stocks)

    def process_stocks(self, stocks):
        with create_pool('process stocks') as pool:
            stocks = pool.map(process_stock, stocks)
        log.info('Processed all stocks')
        return stocks

    def _fetch_stocks(self):
        log.info("Fetch stocks from web")
        stocks = ts.get_stock_basics()
        with create_pool('fetch stocks') as pool:
            ret = pool.map(build_stock, [(i, stock) for i, stock in enumerate(stocks.iterrows())])
            ret = [x for x in ret if x is not None]
            return ret

    def loopback(self):
        # Temporary wipe the stocks in `self` to make the IPC faster
        stocks = self.stocks
        self.stocks = None
        with create_pool('loopback') as pool:
            self.stocks = pool.map(loopback_stock, [(self, stock) for stock in stocks])

    def _select_range(self, df):
        try:
            if self.from_date:
                df = df.loc[df['date'] >= self.from_date]
            if self.to_date:
                df = df.loc[df['date'] <= self.to_date]
        except:
            pass

        return df

    def trade_days(self):
        if self.to_date is None:
            to_date = date.today().strftime('%Y-%m-%d')
        else:
            to_date = self.to_date

        return days_between(self.from_date, to_date) / 7 * 5

    @abstractmethod
    def init_internal_result(self):
        self.ops = []

    @abstractmethod
    def update_internal_result(self, row):
        pass

    def update_operations(self, op):
        self.ops.append(op)

    @abstractmethod
    def calc_loopback_result(self):
        return Result(self.ops)

    def loopback_one(self, stock):
        df = self._select_range(stock.df)
        self.init_internal_result()
        for _, row in df.iterrows():
            op = None
            if self.is_time_to_buy(row):
                op = self.buy(row)
            elif self.is_time_to_stop(row):
                op = self.stop(row)
            elif self.is_time_to_sell(row):
                op = self.sell(row)

            if op is not None:
                self.update_operations(op)

            self.update_internal_result(row)

        # assume sell the stock in the last day
        if op is None:
            op = self.stop(row)
            self.update_operations(op)
        return self.calc_loopback_result()

    @abstractmethod
    def is_time_to_buy(self,row):
        pass

    @abstractmethod
    def is_time_to_sell(self, row):
        pass

    @abstractmethod
    def is_time_to_stop(self, row):
        pass

    @abstractmethod
    def buy(self, row):
        pass

    @abstractmethod
    def sell(self, row):
        pass

    @abstractmethod
    def stop(self, row):
        pass

    @abstractmethod
    def is_time_to_buy(self, row):
        pass

    @abstractmethod
    def is_time_to_sell(self, row):
        pass

    def plot_benefit(self, title, stocks):
        x = [i for i in range(1, len(stocks) + 1)]
        y = [stock.get_benefit_rate() for stock in stocks]
        plt.plot(x, y, 'ro')
        plt.title(title)
        plt.show()

    def plot_hist(self):
        x = [stock.get_benefit() for stock in self.stocks]
        plt.hist(x)
        plt.xlabel('benefit')
        plt.xlim(-3.0, 3.0)
        plt.ylabel('Frequency')
        plt.title('Benefit hist')
        plt.show()

    def run_loopback_one_by_code(self, code):
        df = ts.get_stock_basics()
        try:
            info = df.loc[code]
        except Exception:
            info = {'name': 'unknown'}
        stock = Stock(code, info)
        self.run_loopback_one(stock)

    def run_loopback_one(self, stock):
        process_stock(stock)
        result = self.loopback_one(stock)
        stock.set_loopback_result(result)
        stock.print_loopback_result()

    @abstractmethod
    def print_loopback_condition(self):
        pass

    def best_stocks(self, filt=None):
        period = 'from %s to %s' % (self.from_date, self.to_date if self.to_date else 'now')
        log.info('Best stocks %s, trade days: %d', period, self.trade_days())
        self.print_loopback_condition()
        if filt:
            self.stocks = list(filter(filt, self.stocks))
            log.info('Filter: %s', filt.__doc__)
        self.loopback()
        purchased_stocks = self.stocks
        # We only consider the stock we really purchased
        purchased_stocks = [x for x in purchased_stocks if x.loopback_result is not None and x.loopback_result.ops]
        purchased_stocks = sorted(purchased_stocks, key=lambda x: x.loopback_result.benefit, reverse=True)
        stocks = []
        benefits = []
        # FIXME:
        for stock in purchased_stocks:
            if stock.get_ops():
                stock.print_loopback_result(debug=True)
                stocks.append(stock)
                benefits.append(stock.get_benefit_rate())

        math_expt = avg(benefits)
        # avg_hold_days = avg(hold_days)
        log.info('Benefit mathematical expectation: %.2f%% for %d stocks',
                 math_expt * 100, len(stocks))

        # self.plot_benefit("%s Math expt: %f" % (period, math_expt), stocks)
        # plot_hist(sorted_stocks)

        self.where_is_my_chance()
        # return math_expt, len(stocks), len(benefits), avg_hold_days


    @abstractmethod
    def where_is_my_chance(self):
        pass


