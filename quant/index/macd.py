#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import talib

__author__ = 'Yang Qian'

"""
Created on 02/02/2018
@author: Yang Qian

"""

fastperiod = 12   # 短期EMA平滑天数
slowperiod = 26    # 长期EMA平滑天数
signalperiod = 9    # DEA线平滑天数

def add_macd(df):
    close = np.array([float(x) for x in df['close']])
    diff, dea, macd = talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    df['DIFF'] = diff
    df['MACD'] = macd