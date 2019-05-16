#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from abc import abstractmethod, ABCMeta, abstractproperty
from contextlib import contextmanager
from datetime import datetime, timedelta, date
from multiprocessing import Pool
import tushare as ts
from quant.helpers import is_rising_trend
from quant.logger.logger import log
from quant.peak import Peak
from quant.loopback.result.base import Result
from quant.stock import Stock
import matplotlib.pyplot as plt
from quant.stockmgr import process_stock
from quant.utils import days_between, create_pool
from quant.stockbasis import StockBasisMgr

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

def loopback_stock(info):
    (loopback, stock) = info
    try:
        result = loopback.loopback_one(stock)
        stock.set_loopback_result(result)
    except Exception as e:
        log.exception('Error occur when looping back %s', stock.code)

    return stock


def avg(l):
    return sum(l) / 1.0 / len(l)


class Loopback(object, metaclass=ABCMeta):
    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    def loopback(self, stocks):
        # Temporary wipe the stocks in `self` to make the IPC faster
        with create_pool('loopback') as pool:
            return pool.map(loopback_stock, [(self, stock) for stock in stocks])

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
        op = None
        row = None
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
        if op is None and row is not None:
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

    def plot_hist(self, stocks):
        x = [stock.get_benefit() for stock in stocks]
        plt.hist(x)
        plt.xlabel('benefit')
        plt.xlim(-3.0, 3.0)
        plt.ylabel('Frequency')
        plt.title('Benefit hist')
        plt.show()

    def run_loopback_one_by_code(self, code, name=None):
        if name is None:
            try:
                name = StockBasisMgr.get_stock_name(code)
            except Exception:
                name = 'unknown'
        info = {'name': name}
        stock = Stock(code, info)
        return self.run_loopback_one(stock)

    def run_loopback_one(self, stock):
        process_stock(stock)
        result = self.loopback_one(stock)
        stock.set_loopback_result(result)
        stock.print_loopback_result()
        return stock

    @abstractmethod
    def print_loopback_condition(self):
        pass

    def best_stocks(self, stocks, filt=None):
        period = 'from %s to %s' % (self.from_date, self.to_date if self.to_date else 'now')
        log.info('Best stocks %s, trade days: %d', period, self.trade_days())
        self.print_loopback_condition()
        if filt:
            stocks = list(filter(filt, stocks))
            log.info('Filter: %s', filt.__doc__)
        self.loopback(stocks)
        purchased_stocks = stocks
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

        self.where_is_my_chance(purchased_stocks)
        # return math_expt, len(stocks), len(benefits), avg_hold_days


    @abstractmethod
    def where_is_my_chance(self, stocks):
        pass

    @abstractmethod
    def is_chance_for(self, stock):
        pass
