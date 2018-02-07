#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tushare as ts

from quant.logger.logger import log
from quant.loopback import LoopbackRSI, LoopbackMACD, LoopbackMACD_RSI, LoopbackMACD_MA, LoopbackMA, LoopbackPeak

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

def is_in_zz500():
    codes = get_codes(ts.get_zz500s())

    def _aux(stock):
        return stock.code in codes

    return _aux


def loop_verify(loopback, from_date):
    log.info('loop verify')
    loopback.from_date = from_date
    loopback.to_date = None
    stocks = []
    total_benefit = 0.0
    for stock in loopback.stocks:
        try:
            if stock.get_benefit() <= 0.0:
                break

            loopback.test_loopback_one(stock)
            stocks.append(stock)
            total_benefit += stock.get_benefit()
        except Exception as e:
            pass

    math_expt = total_benefit / len(stocks)

    loopback.plot_benefit("Math expt : %f" % math_expt, stocks)

def test_one_rsi(code, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(None, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.test_loopback_one_by_code(code)


def loopback_rsi(persist_f, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackRSI(persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.init()
    loopback.best_stocks(is_in_hs300())


def test_one_stock_macd(code, from_date, to_date, stop_loss):
    loopback = LoopbackMACD(None, from_date, to_date, stop_loss)
    loopback.test_loopback_one_by_code(code)


def loopback_macd(persist_f, from_date, to_date, stop_loss):
    loopback = LoopbackMACD(persist_f, from_date, to_date, stop_loss)
    loopback.init()
    loopback.best_stocks(is_in_hs300())

    loop_verify(loopback, to_date)


def test_one_stock_macd_ma(code, from_date, to_date, stop_loss):
    loopback = LoopbackMACD_MA(None, from_date, to_date, stop_loss)
    loopback.test_loopback_one_by_code(code)


def loopback_macd_ma(persist_f, from_date, to_date, stop_loss, stop_benefit):
    """Rising trend && macd going up
    """
    loopback = LoopbackMACD_MA(persist_f, from_date, to_date, stop_loss, stop_benefit)
    loopback.init()
    loopback.best_stocks(is_in_hs300())

    loop_verify(loopback, to_date)


def test_one_stock_macd_rsi(code, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackMACD_RSI(None, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.test_loopback_one_by_code(code)


def loopback_macd_rsi(persist_f, from_date, to_date, rsi_period, rsi_buy, rsi_sell, stop_loss):
    loopback = LoopbackMACD_RSI(persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)
    loopback.init()
    loopback.best_stocks(not_startup)

    loop_verify(loopback, to_date)


def test_one_stock_ma(code, from_date, to_date, stop_loss, stop_benefit):
    loopback = LoopbackMA(None, from_date, to_date, stop_loss, stop_benefit, 60)
    loopback.test_loopback_one_by_code(code)


def loopback_ma(persist_f, from_date, to_date, stop_loss, stop_benefit, ma_preiod):
    """ rising trend and ma break ma_preiod
    """
    loopback = LoopbackMA(persist_f, from_date, to_date, stop_loss, stop_benefit, ma_preiod)
    loopback.init()
    loopback.best_stocks(is_in_hs300())

    loop_verify(loopback, to_date)


def test_one_stock_inverse(code, from_date, to_date, stop_loss, stop_benefit):
    loopback = LoopbackPeak(None, from_date, to_date, stop_loss, stop_benefit)
    loopback.test_loopback_one_by_code(code)


def loopback_inverse(persist_f, from_date, to_date, stop_loss, stop_benefit):
    """ rising trend and ma break ma_preiod
    """
    loopback = LoopbackPeak(persist_f, from_date, to_date, stop_loss, stop_benefit)
    loopback.init()
    loopback.best_stocks(is_in_hs300())

    # loop_verify(loopback, to_date)

if __name__ == '__main__':
    d_2016 = '2016-03-03'
    d_2017 = '2017-03-03'
    d_2017_n = '2017-09-01'
    # loopback_rsi(None, '2017-05-09', None, 6, 30.0, 70.0, -0.1)
    # loopback_macd(None, d_2017, None, -0.05)
    # loopback_macd_rsi(None, '2017-05-09', '2017-09-01', 6, 30.0, 70.0, -0.1)

    # rising trend &&  macd up
    # loopback_macd_ma(None, d_2017, None, -0.05, None)

    # rising trend and ma break 60 avg
    # loopback_ma(None, d_2017, None, -0.05, 0.1, 60)

    # rising trend and ma break 180 avg
    # loopback_ma(None, d_2017, None, -0.05, 0.1, 180)

    loopback_inverse(None, d_2017, None, -0.05, 0.1)

    # test_one_rsi('600600', '2017-05-09', None, 6, 20.0, 70.0, -0.1)
    # test_one_stock_macd('600600', '2017-09-01', None, -0.1)
    # test_one_stock_macd_rsi('600600', '2017-05-09', None, 6, 20.0, 70.0, -0.1)
    # test_one_stock_macd_ma('600519', '2017-01-10', None, -0.05)
    # test_one_stock_ma('600600', '2017-09-01', None, -0.1)

    # test_one_stock_inverse('600600', d_2017, None, -0.1, 0.1)
