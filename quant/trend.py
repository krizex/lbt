#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.loopback.trend import LoopbackTrend

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

def run_one(code, from_date, to_date, highest_days_n):
    loopback = LoopbackTrend(None, from_date, to_date, highest_days_n)
    loopback.run_loopback_one_by_code(code)


if __name__ == '__main__':
    d_from = '2016-08-16'
    d_to = '2019-08-16'
    # run_one('600737', d_from, d_to, 11)
    run_one('600201', d_from, d_to, 11)
    # run_one('601318', d_from, d_to, 11)
