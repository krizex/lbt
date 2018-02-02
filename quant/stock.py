#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.logger.logger import log
from quant.macd import add_macd
from quant.rsi import add_rsi

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

    def set_loopback_result(self, result):
        self.loopback_result = result

    def print_loopback_result(self):
        log.info('%s %f%% %s' % (self.code, self.loopback_result.benefit * 100, ' '.join(self.loopback_result.ops)))

    def is_time_to_buy_by_rsi(self, rsi_in):
        return self.df.loc[self.df.shape[0] - 1]['RSI'] <= rsi_in

    def is_time_to_buy_by_macd(self):
        yesterday = self.df.shape[0] - 2
        today = self.df.shape[0] - 1
        return self.df.loc[yesterday]['MACD'] < 0 < self.df.loc[today]['MACD']

    def get_benefit(self):
        return self.loopback_result.benefit

