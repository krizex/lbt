#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

__author__ = 'Yang Qian'

"""
Created on 06/24/2018
@author: Yang Qian

"""


def add_p_change(df):
    close = np.array([float(x) for x in df['close']])
    p_change = close[1:] / close[:-1] - 1
    p_change = np.insert(p_change, 0, 0)
    df['p_change'] = p_change
