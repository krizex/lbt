#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tushare as ts

from quant.logger.logger import log
from quant.loopback import LoopbackRSI, LoopbackMACD, LoopbackMACD_RSI, LoopbackMACD_MA

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

def get_codes(df):
    codes = []
    for x in df.iterrows():
        codes.append(x[1]['code'])

    return codes

def is_in_hs300():
    codes = get_codes(ts.get_hs300s())

    def _aux(stock):
        return stock.code in codes

    return _aux

def is_in_sz50():
    codes = get_codes(ts.get_sz50s())

    def _aux(stock):
        return stock.code in codes

    return _aux


def test_one_stock_rsi(code, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(None, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.test_loopback_one_by_code(code)


def loopback_rsi(persist_f, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.init()
    loopback.best_stocks(is_in_hs300())



def test_one_stock_macd(code, from_date, to_date):
    loopback = LoopbackMACD(None, from_date, to_date)
    loopback.test_loopback_one_by_code(code)


def loopback_macd(persist_f, from_date, to_date, stop_loss):
    loopback = LoopbackMACD(persist_f, from_date, to_date, stop_loss)
    loopback.init()
    loopback.best_stocks(is_in_sz50())

    # loop 2
    log.info('loop 2')
    loopback.from_date = to_date
    loopback.to_date = None
    stocks = []
    total_benefit = 0.0
    for stock in loopback.stocks:
        try:
            loopback.test_loopback_one(stock)
            stocks.append(stock)
            total_benefit += stock.get_benefit()
        except Exception as e:
            pass

    math_expt = total_benefit / len(stocks)

    loopback.plot_benefit("Math expt : %f" % math_expt, stocks)


def loopback_macd_ma(persist_f, from_date, to_date, stop_loss):
    loopback = LoopbackMACD_MA(persist_f, from_date, to_date, stop_loss)
    loopback.init()
    loopback.best_stocks(is_in_sz50())

    # loop 2
    log.info('loop 2')
    loopback.from_date = to_date
    loopback.to_date = None
    stocks = []
    total_benefit = 0.0
    for stock in loopback.stocks:
        try:
            loopback.test_loopback_one(stock)
            stocks.append(stock)
            total_benefit += stock.get_benefit()
        except Exception as e:
            pass

    math_expt = total_benefit / len(stocks)

    loopback.plot_benefit("Math expt : %f" % math_expt, stocks)


def test_one_stock_macd_rsi(code, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackMACD_RSI(None, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.test_loopback_one_by_code(code)


def loopback_macd_rsi(persist_f, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackMACD_RSI(persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.init()
    loopback.best_stocks(not_startup)

    # loop 2
    log.info('loop 2')
    loopback.from_date = to_date
    loopback.to_date = None
    stocks = []
    for stock in loopback.stocks:
        try:
            loopback.test_loopback_one(stock)
            stocks.append(stock)
        except Exception as e:
            pass
    loopback.plot_benefit("loop2", stocks)


if __name__ == '__main__':
    # test_one_stock('600600', '2017-05-09', None, 6, 20.0, 70.0, 0.1)
    # loopback_rsi(None, '2017-05-09', None, 6, 30.0, 70.0, 0.1)
    loopback_macd(None, '2017-10-10', None, 0.01)
    # loopback_macd_ma(None, '2017-01-10', '2017-09-14', 0.1)
    # test_one_stock_macd('600600', '2017-09-01')
    # test_one_stock_macd_rsi('600600', '2017-05-09', None, 6, 20.0, 70.0, 0.1)
    # loopback_macd_rsi(None, '2017-05-09', '2017-09-01', 6, 30.0, 70.0, 0.1)
