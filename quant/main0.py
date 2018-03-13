#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.filters import not_startup, is_in_hs300
from quant.logger.logger import log
from quant.loopback import LoopbackRSI, LoopbackMACD, LoopbackMACD_RSI, LoopbackMACDRisingTrend, LoopbackMA, LoopbackPeak, \
    LoopbackBreakresistance, LoopbackGrid

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


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


def test_one_stock_macd_rising_trend(code, from_date, to_date, stop_loss):
    loopback = LoopbackMACDRisingTrend(None, from_date, to_date, stop_loss)
    loopback.test_loopback_one_by_code(code)


def loopback_macd_rising_trend(persist_f, from_date, to_date, stop_loss, stop_benefit):
    """Rising trend && macd going up
    """
    loopback = LoopbackMACDRisingTrend(persist_f, from_date, to_date, stop_loss, stop_benefit)
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

def loopback_break_resistance(persist_f, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude):
    loopback = LoopbackBreakresistance(persist_f, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude)
    loopback.init()
    loopback.best_stocks(is_in_hs300())

def test_one_stock_break_resistance(code, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude):
    loopback = LoopbackBreakresistance(None, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude)
    loopback.test_loopback_one_by_code(code)


def test_one_stock_grid(code, from_date, to_date, mid, range, size):
    loopback = LoopbackGrid(None, from_date, to_date, None, None, mid, range, size)
    loopback.test_loopback_one_by_code(code)


if __name__ == '__main__':
    d_2015 = '2015-08-14'
    d_2016 = '2016-03-03'
    d_2017 = '2017-03-03'
    d_2017_n = '2017-09-01'
    d_2018 = '2018-01-25'
    # loopback_rsi(None, '2017-05-09', None, 6, 30.0, 70.0, -0.1)
    # loopback_macd(None, d_2017, None, -0.05)
    # loopback_macd_rsi(None, '2017-05-09', '2017-09-01', 6, 30.0, 70.0, -0.1)

    # rising trend &&  macd up
    # loopback_macd_rising_trend(None, d_2017, None, -0.05, None)

    # rising trend and ma break 60 avg
    # loopback_ma(None, d_2017, None, -0.05, 0.3, 60)

    # rising trend and ma break 180 avg
    # loopback_ma(None, d_2015, None, -0.05, 0.3, 180)

    # find inverse peak
    # loopback_inverse(None, d_2017, None, -0.05, 0.1)

    # find break resistance
    # loopback_break_resistance(None, d_2017, None, -0.03, 0.3, 30, 0.05)

    # test_one_rsi('600600', '2017-05-09', None, 6, 20.0, 70.0, -0.1)
    # test_one_stock_macd('600600', '2017-09-01', None, -0.1)
    # test_one_stock_macd_rsi('600600', '2017-05-09', None, 6, 20.0, 70.0, -0.1)
    # test_one_stock_macd_ma('600519', '2017-01-10', None, -0.05)
    # test_one_stock_ma('600600', '2017-09-01', None, -0.1)
    # test_one_stock_inverse('600600', d_2017, None, -0.1, 0.1)

    # test_one_stock_break_resistance('600600', d_2017, None, -0.03, 0.1, 30, 0.1)

    d_2016 = '2016-08-16'
    d_2017 = '2017-08-16'
    # test_one_stock_grid('159922', d_2017, d_2018, 6.5, 0.3, 20)
    # test_one_stock_grid('512000', d_2017, d_2018, 1.038, 0.3, 30)
    # test_one_stock_grid('162411', '2017-04-10', '2018-01-22', 0.567, 0.3, 20)
    # test_one_stock_grid('510110', '2016-04-06', '2017-04-25', 3.0, 0.5, 20)
    # test_one_stock_grid('159922', '2016-05-11', d_2017, 6.3, 0.3, 20)
    # test_one_stock_grid('601601', '2017-11-30', '2018-02-26', 40, 0.25, 10)
    # test_one_stock_grid('002415', '2017-11-30', '2018-02-27', 40, 0.25, 10)
    # test_one_stock_grid('512000', '2017-09-04', '2018-03-12', 0.911, 0.10, 20)
    # test_one_stock_grid('159929', '2017-09-04', '2018-02-27', 1.556, 0.10, 20)
    test_one_stock_grid('512000', '2017-09-04', '2018-03-12', 0.848, 0.1, 30)

