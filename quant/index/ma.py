#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 02/03/2018
@author: Yang Qian

"""

import numpy as np
import talib


def add_ma(df, period):
    close = np.array([float(x) for x in df['close']])
    df['MA'] = talib.SMA(close, timeperiod=period)
