#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.loopback import LoopbackRSI

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def filter_out_startup(stock):
    return not (stock.code.startswith('300') or stock.code.startswith('002'))


def loopback_rsi(persist_f, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(persist_f, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss)
    loopback.init()
    loopback.best_stocks(filter_out_startup)


def test_one_stock(code, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(None, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss)
    loopback.test_loopback_one(code)

if __name__ == '__main__':
    # test_one_stock('600600', '2017-05-09', 6, 20.0, 70.0, 0.1)
    loopback_rsi(None, '2017-05-09', 6, 20.0, 70.0, 0.1)
