#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 02/03/2018
@author: Yang Qian

"""

import numpy as np
import talib


def add_ma(df):
    close = np.array([float(x) for x in df['close']])
    df['MA20'] = talib.SMA(close, timeperiod=20)
    df['MA60'] = talib.SMA(close, timeperiod=60)
    df['MA180'] = talib.SMA(close, timeperiod=180)
    # sma of MA60
    ma60 = np.array([float(x) for x in df['MA60']])
    # df['MA60/120'] = talib.SMA(ma60, timeperiod=120)
    df['MA60/60'] = talib.SMA(ma60, timeperiod=60)
    ma20 = np.array([float(x) for x in df['MA20']])
    df['MA20/20'] = talib.SMA(ma20, timeperiod=20)
