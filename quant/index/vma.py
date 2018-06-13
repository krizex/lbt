#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 06/12/2018
@author: Yang Qian

"""

import numpy as np
import talib


def add_vma(df):
    volume = np.array([float(x) for x in df['volume']])
    df['V_MA5'] = talib.SMA(volume, timeperiod=5)
    df['V_MA10'] = talib.SMA(volume, timeperiod=10)
    df['V_MA20'] = talib.SMA(volume, timeperiod=20)