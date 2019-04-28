#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 02/06/2018
@author: Yang Qian

"""


def is_rising_trend(row):
    return all([
            row['MA20'] > row['MA20/20'],
            row['MA60'] > row['MA60/60'],
        ])
