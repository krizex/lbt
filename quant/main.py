#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.loopback import LoopbackRSI, LoopbackMACD

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def not_startup(stock):
    return not (stock.code.startswith('300') or stock.code.startswith('002'))


def pe_less_than(pe):
    return lambda stock: stock.pe < pe

def not_startup_and_pe_less_than(pe):
    return lambda x: not_startup(x) and pe_less_than(pe)(x)


def loopback_rsi(persist_f, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(persist_f, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss)
    loopback.init()
    loopback.best_stocks(not_startup_and_pe_less_than(30))
    loopback.plot_pe()


def test_one_stock_rsi(code, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(None, from_date, rsi_period, rsi_buy, rsi_sell, stop_loss)
    loopback.test_loopback_one(code)


def test_one_stock_macd(code, from_date):
    loopback = LoopbackMACD(None, from_date)
    loopback.test_loopback_one(code)


def loopback_macd(persist_f, from_date):
    loopback = LoopbackMACD(persist_f, from_date)
    loopback.init()
    loopback.best_stocks(not_startup)


if __name__ == '__main__':
    # test_one_stock('600600', '2017-05-09', 6, 20.0, 70.0, 0.1)
    # loopback_rsi(None, '2017-05-09', 6, 30.0, 70.0, 0.1)
    loopback_macd(None, '2017-09-01')
    # test_one_stock_macd('600600', '2017-05-09')
