#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""
import numpy as np
import talib


def add_rsi(df, period):
    close = [float(x) for x in df['close']]
    df['RSI'] = talib.RSI(np.array(close), timeperiod=period)
    return df




