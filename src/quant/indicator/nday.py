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
    df['MAX_%d' % n] = df['close'].rolling(window=n, center=False).max().shift(1)


def add_nday_min(df, n):
    df['MIN_%d' % n] = df['close'].rolling(window=n, center=False).min().shift(1)