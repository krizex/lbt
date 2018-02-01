#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.logger.logger import log
from quant.rsi import add_rsi

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

import tushare as ts


class LoopbackResult(object):
    def __init__(self, benefit, ops):
        self.benefit = benefit
        self.ops = ops


class Stock(object):
    def __init__(self, code):
        self.code = code
        self.df = ts.get_k_data(code)
        self.loopback_result = None

    def add_rsi(self, period):
        self.df = add_rsi(self.df, period)

    def set_loopback_result(self, benefit, ops):
        self.loopback_result = LoopbackResult(benefit, ops)

    def print_loopback_result(self):
        log.info('%s %f%% %s' % (self.code, self.loopback_result.benefit * 100, ' '.join(self.loopback_result.ops)))

    def is_time_to_buy(self, rsi_in):
        return self.df.loc[self.df.shape[0] - 1]['RSI'] <= rsi_in

    def get_benefit(self):
        return self.loopback_result.benefit

def get_all_stocks():
    return ts.get_stock_basics()


def get_all_stock_code():
    df = get_all_stocks()
    return [index for index, _ in df.iterrows()]

