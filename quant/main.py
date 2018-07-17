#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cPickle as pickle
import signal

from quant.filters import is_in_hs300, is_in_sz50, not_startup, is_in_zz500
from quant.logger.logger import log
from quant.loopback import LoopbackMACDRisingTrend, LoopbackPeak, LoopbackBreakresistance, LoopbackTrend, g_pool, \
    setup_signal_handler, terminate_pool_and_exit, LoopbackPriceVol, LoopbackBreak

__author__ = 'Yang Qian'

"""
Created on 02/22/2018
@author: Yang Qian

"""


def loopback_macd_rising_trend(persist_f, from_date, to_date, stop_loss, stop_benefit):
    """Rising trend && macd going up
    """
    loopback = LoopbackMACDRisingTrend(persist_f, from_date, to_date, stop_loss, stop_benefit)
    loopback.init()
    loopback.best_stocks(is_in_sz50())


def loopback_break_resistance(persist_f, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude):
    loopback = LoopbackBreakresistance(persist_f, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude)
    loopback.init()
    loopback.best_stocks(is_in_hs300())


def loopback_inverse(persist_f, from_date, to_date, stop_loss, stop_benefit):
    """ Rising trend and ma break ma_preiod
    """
    loopback = LoopbackPeak(persist_f, from_date, to_date, stop_loss, stop_benefit)
    loopback.init()
    loopback.best_stocks()


def loopback_trend(saved_stocks, persist_f, from_date, to_date, stop_loss, stop_benefit, min_up_days, close_ma, volume_ma='volume', volume_ratio=0.8):
    """Rising trend
    """
    loopback = LoopbackTrend(persist_f, from_date, to_date, stop_loss, stop_benefit, min_up_days, close_ma, volume_ma, volume_ratio)
    if saved_stocks is not None:
        log.debug('recover from saved stocks')
        loopback.stocks = saved_stocks
    else:
        loopback.init()
    return loopback.best_stocks(is_in_hs300())


def loopback_vol_price(persist_f, from_date, to_date, stop_loss, stop_benefit, vol_expand):
    loopback = LoopbackPriceVol(persist_f, from_date, to_date, stop_loss, stop_benefit, vol_expand)
    loopback.init()
    loopback.best_stocks(is_in_hs300())


def print_parameter(prefix, (math_expect, stocks_cnt, ops_cnt, avg_hold_days, stop_rate, days)):
    log.info('%s: stop_rate %f%%, continue days %d, '
             'math expect: %f%%, stocks count: %d, operations count: %d, avg hold days: %f',
             prefix, stop_rate * 100, days, math_expect * 100, stocks_cnt, ops_cnt, avg_hold_days)


def find_x(start_date, (stop_start, stop_end, stop_step), (days_min, days_max, days_step)):
    loopback = LoopbackTrend(None, start_date, None, -stop_start, stop_start, days_min, 'MA5', 'V_MA10', 1)
    loopback.init()
    saved_stocks = loopback.stocks
    stop_rate = stop_start
    rets = []
    while stop_rate <= stop_end:
        days = days_min
        while days <= days_max:
            try:
                math_expt, stock_cnt, op_cnt, avg_hold_days = loopback_trend(saved_stocks, None, start_date, None, -stop_rate, stop_rate, days, 'MA5', 'V_MA10', 1)
                if op_cnt >= loopback.trade_days():
                    rets.append((math_expt, stock_cnt, op_cnt, avg_hold_days, stop_rate, days))
                    rets = sorted(rets, key=lambda x: x[0], reverse=True)
                    best = rets[0]
                    print_parameter('Current best parameter', best)
            except:
                log.exception('error happen')
            days += days_step
        stop_rate += stop_step

    rets = sorted(rets, key=lambda x: x[0], reverse=True)
    best = rets[0]
    print_parameter('Best parameter', best)
    for ret in rets:
        print_parameter('All items', ret)

    with open('results.dat', 'w') as f:
            pickle.dump(rets, f)


def loopback_break_ndays(persist_f, from_date, to_date, stop_loss, stop_benefit):
    loopback = LoopbackBreak(persist_f, from_date, to_date, stop_loss, stop_benefit)
    loopback.init()
    return loopback.best_stocks(is_in_hs300())


def main():
    d_2017 = '2017-06-01'
    d_2018 = '2018-01-04'
    # stop_rate = 0.007
    stop_rate = 0.031
    continue_days = 5
    # rising trend &&  macd up
    # loopback_macd_rising_trend(None, d_2017, None, -0.05, None)

    # find inverse peak
    # loopback_inverse(None, d_2017, None, -0.05, 0.1)

    # find break resistance
    # loopback_break_resistance(None, d_2017, None, -0.03, 0.3, 30, 0.05)

    # loopback_trend(None, None, d_2018, None, -stop_rate, stop_rate, continue_days, 'MA5', 'V_MA10', 1)
    # find_x(d_2018, (0.005, 0.05, 0.001), (3, 10, 1))

    loopback_break_ndays(None, d_2018, None, -1, 1)


if __name__ == '__main__':
    main()

