#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.loopback.trend import LoopbackTrend
from quant.filters import is_in_hs300, is_in_sz50, not_startup, is_in_zz500, get_codes
from quant.stockmgr import StockMgr
import tushare as ts
from quant.logger.logger import log

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

def run_one(code, from_date, to_date, highest_days_n):
    loopback = LoopbackTrend(from_date, to_date, highest_days_n)
    loopback.run_loopback_one_by_code(code)


def run_with_filter(from_date, to_date, highest_days_n, filt):
    stockmgr = StockMgr(None)
    loopback = LoopbackTrend(from_date, to_date, highest_days_n)
    loopback.best_stocks(filt, stockmgr.stocks)


def find_chances(from_date, to_date, highest_days_n):
    rets = []
    codes = get_codes(ts.get_hs300s())
    for code in codes:
        loopback = LoopbackTrend(from_date, to_date, highest_days_n)
        stock = loopback.run_loopback_one_by_code(code)
        if loopback.is_chance_for(stock):
            rets.append(stock)

    codes = [
        ('162411', 'HBYQ'),
        ('512000', 'QS-ETF'),
        ('501029', 'BPHL'),
        ('510050', '50-ETF'),
        ('518880', 'GOLD-ETF'),
        ('513030', 'DAX'),
    ]

    for code, name in codes:
        loopback = LoopbackTrend(from_date, to_date, highest_days_n)
        stock = loopback.run_loopback_one_by_code(code, name)
        if loopback.is_chance_for(stock):
            rets.append(stock.get_loopback_result())

    log.info('==========Your chances ==========')
    for stock in rets:
        log.info(stock)

    return rets


def run_individals():
    run_one('600737', d_from, d_to, 22)
    run_one('600201', d_from, d_to, 22)
    run_one('000977', d_from, d_to, 22)
    run_one('601318', d_from, d_to, 22)
    run_one('501029', d_from, d_to, 22)
    run_one('510050', d_from, d_to, 22)
    run_one('000063', d_from, d_to, 22)
    run_one('600498', d_from, d_to, 22)


d_from = '2016-08-16'
d_to = '2019-08-16'

if __name__ == '__main__':
    # run_individals()
    # run_with_filter(d_from, d_to, 22, is_in_hs300())
    find_chances(d_from, d_to, 22)
