#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.helpers import is_rising_trend
from quant.index.ma import add_ma
from quant.index.rsi import add_rsi
from quant.index.macd import add_macd
from quant.logger.logger import log

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

import tushare as ts


class Stock(object):
    def __init__(self, code, info):
        self.code = code
        self.info = info
        self.df = ts.get_k_data(code, retry_count=10)
        self.loopback_result = None

    @property
    def pe(self):
        return self.info['pe']

    def add_rsi(self, period):
        add_rsi(self.df, period)

    def add_macd(self):
        add_macd(self.df)

    def add_ma(self):
        add_ma(self.df)

    def set_loopback_result(self, result):
        self.loopback_result = result

    def print_loopback_result(self):
        log.info('%s %s %f%%' % (self.code, self.info['name'].decode('utf8'), self.loopback_result.benefit * 100))
        if self.loopback_result.hold_days:
            log.info('hold %d days', self.loopback_result.hold_days)
        for op in self.loopback_result.ops:
            log.info('%s %s %f%%', op.op_in, op.op_out, op.benefit * 100)

    def get_last_op(self):
        if not self.loopback_result:
            return None

        return self.loopback_result.ops[-1]

    def is_time_to_buy_by_rsi(self, rsi_in):
        today = self.df.shape[0] - 1
        return self.df.loc[today]['RSI'] <= rsi_in

    def is_time_to_buy_by_macd(self):
        yesterday = self.df.shape[0] - 2
        today = self.df.shape[0] - 1
        return self.df.loc[yesterday]['MACD'] < 0 < self.df.loc[today]['MACD'] and self.df.loc[today]['DIFF'] > 0.0

    def is_rising_trend_now(self):
        today = self.df.shape[0] - 1
        row = self.df.loc[today]
        return is_rising_trend(row)

    def is_time_to_buy_by_ma(self, ma):
        yesterday = self.df.shape[0] - 2
        today = self.df.shape[0] - 1

        def gap(day):
            return self.df.loc[day]['close'] - self.df.loc[day][ma]

        return gap(yesterday) <= 0.0 < gap(today)

    def is_time_to_buy_by_break_resistance(self, date_range, amplitude):
        from quant.loopback import LoopbackBreakresistance
        today = self.df.shape[0] - 1
        start = today - date_range
        df = self.df[start:today]
        data = [row for _, row in df.iterrows()]
        if self.df.loc[today]['close'] > LoopbackBreakresistance.calc_highest_price(data) and \
                LoopbackBreakresistance.data_in_amplitude(data, amplitude):
            return True

        return False

    def get_benefit(self):
        return self.loopback_result.benefit

    def calc_trend_day_cnt(self):
        cnt = 0
        for idx in reversed(self.df.ndex):
            row = self.df.loc[idx]
            if row['close'] >= row['MA10']:
                cnt += 1
            else:
                break

        return cnt

