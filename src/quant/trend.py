#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from quant.loopback.trend import LoopbackTrend
from quant.filters import is_in_hs300, is_in_sz50, not_startup, is_in_zz500, get_codes
from quant.stockmgr import StockMgr
import tushare as ts
from quant.logger.logger import log
from quant.stockbasis import StockBasisMgr

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


def _loopback_stock(code, name, from_date, to_date, highest_days_n):
    loopback = LoopbackTrend(from_date, to_date, highest_days_n)
    stock = loopback.run_loopback_one_by_code(code, name)
    return stock, loopback.is_chance_for(stock), loopback.cur_price_pos_in_history(stock)



def get_customize_codes():
    for _ in range(10):
        try:
            js = []
            resp = requests.get('http://lamp:8000/trend/records/')
            js += resp.json()
            resp = requests.get('http://lamp:8000/rebound/records/')
            js += resp.json()
            return js
        except:
            time.sleep(10)


def find_chances(from_date, to_date, highest_days_n):
    def _in_list(code, l):
        for c, _ in l:
            if code == c:
                return True
        return False

    # customize
    js = get_customize_codes()
    log.info('customize stocks: %s', js)
    codes = js

    for code in get_codes(ts.get_hs300s()):
        if _in_list(code, codes):
            continue
        else:
            codes.append((code, None))

    rets = []
    cur_pos_rets = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [executor.submit(_loopback_stock, code, name, from_date, to_date, highest_days_n) for code, name in codes]
        for task in as_completed(tasks):
            stock, is_chance, cur_pos = task.result()
            if is_chance:
                rets.append(stock)

            if cur_pos <= 0.2:
                cur_pos_rets.append((cur_pos, stock))

    rets.sort(key=lambda s: s.get_benefit_rate(), reverse=True)
    log.info('==========Your chances==========')
    for stock in rets:
        log.info(stock)

    cur_pos_rets.sort(key=lambda s: s[0])
    log.info('==========Underestimate==========')
    for _, stock in rets:
        log.info(stock)

    return rets, cur_pos_rets


def run_individals():
    run_one('600737', d_from, None, 22)
    run_one('600201', d_from, None, 22)
    run_one('000977', d_from, None, 22)
    run_one('601318', d_from, None, 22)
    run_one('501029', d_from, None, 22)
    run_one('510050', d_from, None, 22)
    run_one('000063', d_from, None, 22)
    run_one('600498', d_from, None, 22)


d_from = '2016-08-16'

if __name__ == '__main__':
    run_individals()
    # find_chances(d_from, None, 22)
