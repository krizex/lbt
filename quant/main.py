#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.filters import is_in_hs300, is_in_sz50
from quant.loopback import LoopbackMACDRisingTrend, LoopbackPeak, LoopbackBreakresistance, LoopbackTrend

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


def loopback_trend(persist_f, from_date, to_date, stop_loss, stop_benefit, min_up_days, index):
    """Rising trend
    """
    loopback = LoopbackTrend(persist_f, from_date, to_date, stop_loss, stop_benefit, min_up_days, index)
    loopback.init()
    loopback.best_stocks()


if __name__ == '__main__':
    d_2017 = '2017-03-03'
    # rising trend &&  macd up
    # loopback_macd_rising_trend(None, d_2017, None, -0.05, None)

    # find inverse peak
    # loopback_inverse(None, d_2017, None, -0.05, 0.1)

    # find break resistance
    # loopback_break_resistance(None, d_2017, None, -0.03, 0.3, 30, 0.05)

    loopback_trend(None, d_2017, None, -0.2, 0.2, 10, 'MA5')