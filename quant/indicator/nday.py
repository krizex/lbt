#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

__author__ = 'Yang Qian'

"""
Created on 07/16/2018
@author: Yang Qian

"""


def add_nday_max(df, n):
    df['MAX_%d' % n] = pd.rolling_max(df['close'], window=n)
    # values = []
    # MAX = []
    # init = False
    #
    # for _, row in df.iterrows():
    #     if not init:
    #         values.append(row['close'])
    #         MAX.append(row['close'] + 1)
    #         if len(values) == n:
    #             init = True
    #     else:
    #         MAX.append(max(values))
    #         del values[0]
    #         values.append(row['close'])
    #
    # df['MAX_%d' % n] = np.array(MAX)


def add_nday_min(df, n):
    # values = []
    # MIN = []
    # init = False
    #
    # for _, row in df.iterrows():
    #     if not init:
    #         values.append(row['close'])
    #         MIN.append(row['close'] - 1)
    #         if len(values) == n:
    #             init = True
    #     else:
    #         MIN.append(min(values))
    #         del values[0]
    #         values.append(row['close'])
    #
    # df['MIN_%d' % n] = np.array(MIN)
    df['MAX_%d' % n] = pd.rolling_min(df['close'], window=n)