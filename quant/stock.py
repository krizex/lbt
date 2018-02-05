#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.index.ma import add_ma
from quant.index.rsi import add_rsi
from quant.index.macd import add_macd
from quant.logger.logger import log

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

import tushare as ts


class Stock(object):
    def __init__(self, code, info):
        self.code = code
        self.info = info
        self.df = ts.get_k_data(code)
        self.loopback_result = None

    @property
    def pe(self):
        return self.info['pe']

    def add_rsi(self, period):
        add_rsi(self.df, period)

    def add_macd(self):
        add_macd(self.df)

    def add_ma(self, period):
        add_ma(self.df, period)

    def set_loopback_result(self, result):
        self.loopback_result = result

    def print_loopback_result(self):
        log.info('%s %s %f%%' % (self.code, self.info['name'].decode('utf8'), self.loopback_result.benefit * 100))
        for op in self.loopback_result.ops:
            log.info('%s %s %f%%', op.op_in, op.op_out, op.benefit * 100)

    def is_time_to_buy_by_rsi(self, rsi_in):
        today = self.df.shape[0] - 1
        return self.df.loc[today]['RSI'] <= rsi_in

    def is_time_to_buy_by_macd(self):
        yesterday = self.df.shape[0] - 2
        today = self.df.shape[0] - 1
        return self.df.loc[yesterday]['MACD'] < 0 < self.df.loc[today]['MACD'] and self.df.loc[today]['DIFF'] > 0.0

    def is_time_to_buy_by_ma(self):
        today = self.df.shape[0] - 1
        return self.df.loc[today]['close'] <= self.df.loc[today]['MA']

    def get_benefit(self):
        return self.loopback_result.benefit

