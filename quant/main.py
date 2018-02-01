#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from quant.logger.logger import log
from quant.stock import Stock, get_all_stock_code
import cPickle as pickle
import matplotlib.pyplot as plt

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def persiste_f_name():
    now = int(time.time())
    time_array = time.localtime(now)
    t = time.strftime("%Y-%m-%d", time_array)
    return 'stocks-%s.dat' % t


def read_stocks_from(persist_f):
    log.info("Read stocks from file:%s", persist_f)
    with open(persist_f) as f:
        return pickle.load(f)


def persist_stocks(persist_f, data):
    log.info("Persist stocks to file:%s", persist_f)
    with open(persist_f, 'w') as f:
        pickle.dump(data, f)


def get_stocks_with_rsi(period):
    persist_f = persiste_f_name()
    if os.path.isfile(persist_f):
        return read_stocks_from(persist_f)
    else:
        return _get_stocks_with_rsi(period, persist_f)


def _get_stocks_with_rsi(period, persist_f):
    log.info("Read stocks from web")
    ret = []
    code_list = get_all_stock_code()
    for i, code in enumerate(code_list):
        log.debug('%d Fetching %s', i, code)
        try:
            stock = Stock(code)
            stock.add_rsi(period)
            ret.append(stock)
        except Exception as e:
            log.error('Error fetching %s', code)

    persist_stocks(persist_f, ret)

    return ret


def loopback_test_one(df, from_date, rsi_in, rsi_out):
    row = df.loc[df['date'] == from_date]
    df = df[row.index[0]:]
    hold = False
    benefit = 1.0
    ops = []
    in_price = 0.0
    out_price = 0.0
    for _, row in df.iterrows():
        if not hold:
            if row['RSI'] <= rsi_in:
                in_price = row['close']
                hold = True
                ops.append("(+)" + row['date'])
        else:
            if row['RSI'] >= rsi_out:
                out_price = row['close']
                benefit = benefit * (out_price / in_price)
                hold = False
                ops.append("(-)" + row['date'])

    return benefit - 1, ops


def loopback_test(stock_list, from_date, rsi_in, rsi_out):
    for stock in stock_list:
        try:
            benefit, ops = loopback_test_one(stock.df, from_date, rsi_in, rsi_out)
            stock.set_loopback_result(benefit, ops)
        except Exception as e:
            pass

    return stock_list


def plot_benefit(stocks):
    x = [i for i in range(1, len(stocks) + 1)]
    y = [stock.get_benefit() for stock in stocks]
    plt.plot(x, y, 'ro')
    plt.show()


def plot_hist(stocks):
    x = [stock.get_benefit() for stock in stocks]
    plt.hist(x)
    plt.xlabel('benefit')
    plt.xlim(-3.0,3.0)
    plt.ylabel('Frequency')
    plt.title('Benefit hist')
    plt.show()


def best_stocks(from_date, rsi_period, rsi_in, rsi_out, filt=None):
    log.info('Best stocks from %s, RSI:%d, RSI_BUY:%d, RSI_SELL:%d', from_date, rsi_period, rsi_in, rsi_out)
    stock_list = get_stocks_with_rsi(rsi_period)
    log.debug('Fetched all stocks')
    stocks = loopback_test(stock_list, from_date, rsi_in, rsi_out)
    stocks = filter(lambda x: x.loopback_result is not None, stocks)
    if filt:
        stocks = filter(filt, stocks)
    sorted_stocks = sorted(stocks, key=lambda x: x.loopback_result.benefit, reverse=True)
    total_benefit = 0.0
    for stock in sorted_stocks:
        stock.print_loopback_result()
        total_benefit += stock.get_benefit()

    plot_benefit(sorted_stocks)
    # plot_hist(sorted_stocks)
    log.info('Benefit mathematical expectation: %f', total_benefit / len(sorted_stocks))

    log.info("=====It's time to buy=====")

    for i, stock in enumerate(sorted_stocks):
        if stock.is_time_to_buy(rsi_in):
            log.info('%d:', i+1)
            stock.print_loopback_result()


def my_test(code):
    stock = Stock(code)
    stock.add_rsi(6)
    stocks = loopback_test([stock], '2017-11-23', 30.0, 80.0)
    for stock in stocks:
        stock.print_loopback_result()


def filter_out_startup(stock):
    return not (stock.code.startswith('300') or stock.code.startswith('002'))

if __name__ == '__main__':
    # my_test('600660')
    best_stocks('2017-05-09', 6, 20.0, 80.0, filter_out_startup)
