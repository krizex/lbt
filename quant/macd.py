#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import talib

__author__ = 'Yang Qian'

"""
Created on 02/02/2018
@author: Yang Qian

"""

short_win = 12   # 短期EMA平滑天数
long_win = 26    # 长期EMA平滑天数
macd_win = 9    # DEA线平滑天数

def add_macd(df):
    close = np.array([float(x) for x in df['close']])
    macd_tmp = talib.MACD(close, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
    DIF = macd_tmp[0]
    DEA = macd_tmp[1]
    MACD = macd_tmp[2]
    df['MACD'] = MACD