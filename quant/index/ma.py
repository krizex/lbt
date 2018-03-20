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
