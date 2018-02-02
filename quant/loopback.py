#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from abc import abstractmethod, ABCMeta, abstractproperty
import tushare as ts

from quant.logger.logger import log
from quant.stock import Stock
import cPickle as pickle
import matplotlib.pyplot as plt

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

class LoopbackResult(object):
    def __init__(self, benefit, ops):
        self.benefit = benefit
        self.ops = ops


class Loopback(object):
    __metaclass__ = ABCMeta

    def __init__(self, persist_f, from_date):
        self.persist_f = self.persiste_f_name(persist_f)
        self.from_date = from_date
        self.stocks = None

    def init(self):
        self.stocks = self.fetch_stocks()

    @abstractmethod
    def process_stock(self, stock):
        pass

    @abstractproperty
    def mytype(self):
        pass

    def persiste_f_name(self, name):
        if name:
            return name
        now = int(time.time())
        time_array = time.localtime(now)
        t = time.strftime("%Y-%m-%d", time_array)
        return 'stocks-%s-%s.dat' % (self.mytype, t)

    def read_stocks_from_persist(self):
        log.info("Read stocks from file:%s", self.persist_f)
        with open(self.persist_f) as f:
            return pickle.load(f)

    def persist_stocks(self, data):
        log.info("Persist stocks to file:%s", self.persist_f)
        with open(self.persist_f, 'w') as f:
            pickle.dump(data, f)

    def fetch_stocks(self):
        if os.path.isfile(self.persist_f):
            stocks = self.read_stocks_from_persist()
        else:
            stocks = self._fetch_stocks()
            self.persist_stocks(stocks)

        log.info('Fetched all stocks')
        return stocks

    def _fetch_stocks(self):
        log.info("Fetch stocks from web")
        ret = []
        stocks = ts.get_stock_basics()
        for i, (code, info) in enumerate(stocks.iterrows()):
            log.debug('%d Fetching %s', i, code)
            try:
                stock = Stock(code, info)
                self.process_stock(stock)
                ret.append(stock)
            except Exception as e:
                log.error('Error fetching %s', code)

        return ret

    def loopback(self):
        for stock in self.stocks:
            try:
                ret = self.loopback_one(stock)
                stock.set_loopback_result(ret)
            except Exception as e:
                pass

    @abstractmethod
    def loopback_one(self, stock):
        pass

    def plot_benefit(self, title):
        x = [i for i in range(1, len(self.stocks) + 1)]
        y = [stock.get_benefit() for stock in self.stocks]
        plt.plot(x, y, 'ro')
        plt.title(title)
        plt.show()

    def plot_hist(self):
        x = [stock.get_benefit() for stock in self.stocks]
        plt.hist(x)
        plt.xlabel('benefit')
        plt.xlim(-3.0,3.0)
        plt.ylabel('Frequency')
        plt.title('Benefit hist')
        plt.show()

    def test_loopback_one(self, code):
        stock = Stock(code, None)
        self.process_stock(stock)
        result = self.loopback_one(stock)
        stock.set_loopback_result(result)
        stock.print_loopback_result()

    @abstractmethod
    def print_loopback_condition(self):
        pass

    def best_stocks(self, filt=None):
        log.info('Best stocks from %s', self.from_date)
        self.print_loopback_condition()
        if filt:
            self.stocks = filter(filt, self.stocks)
        self.loopback()
        self.stocks = filter(lambda x: x.loopback_result is not None, self.stocks)
        self.stocks = sorted(self.stocks, key=lambda x: x.loopback_result.benefit, reverse=True)
        total_benefit = 0.0
        for stock in self.stocks:
            stock.print_loopback_result()
            total_benefit += stock.get_benefit()

        math_expt = total_benefit / len(self.stocks)
        log.info('Benefit mathematical expectation: %f', math_expt)

        self.plot_benefit("Math expt: %f" % math_expt)
        # plot_hist(sorted_stocks)

        self.where_is_my_chance()

    @abstractmethod
    def where_is_my_chance(self):
        pass


class LoopbackRSI(Loopback):
    def __init__(self, persist_f, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
        super(LoopbackRSI, self).__init__(persist_f, from_date)
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
        self.stop_loss = stop_loss

    def process_stock(self, stock):
        stock.add_rsi(self.rsi_period)

    @property
    def mytype(self):
        return 'RSI'

    def loopback_one(self, stock):
        df = stock.df
        row = df.loc[df['date'] == self.from_date]
        df = df[row.index[0]:]
        hold = False
        benefit = 1.0
        ops = []
        in_price = 0.0
        for _, row in df.iterrows():
            if not hold:
                if row['RSI'] <= self.rsi_buy:
                    in_price = row['close']
                    hold = True
                    ops.append("(+)" + row['date'])
            else:
                out_price = row['close']
                cur_benefit = out_price / in_price
                if row['RSI'] >= self.rsi_sell:
                    benefit *= cur_benefit
                    hold = False
                    ops.append("(-)" + row['date'])
                elif cur_benefit + self.stop_loss < 1.0:
                    benefit *= cur_benefit
                    hold = False
                    ops.append("(!-)" + row['date'])

        return LoopbackResult(benefit - 1, ops)

    def print_loopback_condition(self):
        log.info('Loopback condition: rsi_period=%d, rsi_buy=%d, rsi_sell=%d, stop_loss=%f',
                 self.rsi_period, self.rsi_buy, self.rsi_sell, self.stop_loss)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_rsi(self.rsi_buy):
                log.info('%d:', i+1)
                stock.print_loopback_result()

    def plot_pe(self):
        x = [i for i in range(1, len(self.stocks) + 1)]
        y = [stock.pe for stock in self.stocks]
        plt.plot(x, y, 'ro')
        plt.title("pe")
        plt.show()


class LoopbackMACD(Loopback):
    def __init__(self, persist_f, from_date):
        super(LoopbackMACD, self).__init__(persist_f, from_date)

    def process_stock(self, stock):
        stock.add_macd()

    @property
    def mytype(self):
        return 'MACD'

    def loopback_one(self, stock):
        df = stock.df
        row = df.loc[df['date'] == self.from_date]
        df = df[row.index[0]:]
        macd_last = 1.0
        hold = False
        benefit = 1.0
        ops = []
        in_price = 0.0
        for _, row in df.iterrows():
            if not hold:
                if macd_last < 0.0 < row['MACD']:
                    in_price = row['close']
                    hold = True
                    ops.append("(+)" + row['date'])
            else:
                if row['MACD'] < 0.0 <= macd_last:
                    out_price = row['close']
                    cur_benefit = out_price / in_price
                    benefit *= cur_benefit
                    hold = False
                    ops.append("(-)" + row['date'])
                # elif cur_benefit + self.stop_loss < 1.0:
                #     benefit *= cur_benefit
                #     hold = False
                #     ops.append("(!-)" + row['date'])

            macd_last = row['MACD']


        return LoopbackResult(benefit - 1, ops)

    def print_loopback_condition(self):
        log.info('Loopback condition: MACD')

    def where_is_my_chance(self):
        log.info("=====Your chance=====")
        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_macd():
                log.info('%d:', i+1)
                stock.print_loopback_result()
