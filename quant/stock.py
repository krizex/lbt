#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.helpers import is_rising_trend
from quant.indicator.change import add_p_change
from quant.indicator.ma import add_ma
from quant.indicator.rsi import add_rsi
from quant.indicator.macd import add_macd
from quant.indicator.vma import add_vma
from quant.indicator.nday import add_nday_max, add_nday_min
from quant.logger.logger import log

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""

import tushare as ts


class Stock(object):
    MAX_INCR = 9.9 / 100

    def __init__(self, code, info):
        self.code = code
        self.info = info
        self.df = ts.get_k_data(code, retry_count=10)
        self.loopback_result = None

    @property
    def pe(self):
        return self.info['pe']

    @property
    def name(self):
        try:
            return self.info['name'].decode('utf8')
        except:
            return 'UNKNOWN'

    def process(self):
        self.add_macd()
        self.add_ma()
        self.add_vma()
        self.add_p_change()
        self.add_nday_max(22)
        self.add_nday_min(11)

    def add_rsi(self, period):
        add_rsi(self.df, period)

    def add_macd(self):
        add_macd(self.df)

    def add_ma(self):
        add_ma(self.df)

    def add_vma(self):
        add_vma(self.df)

    def add_p_change(self):
        add_p_change(self.df)

    def add_nday_max(self, n):
        add_nday_max(self.df, n)

    def add_nday_min(self, n):
        add_nday_min(self.df, n)

    def set_loopback_result(self, result):
        self.loopback_result = result

    def print_loopback_result(self, debug=False):
        if debug:
            output_log = log.debug
        else:
            output_log = log.info
        output_log('%s %s %f%%' % (self.code, self.name, self.loopback_result.benefit * 100))
        if self.loopback_result.hold_days:
            output_log('hold %d days', self.loopback_result.hold_days)
        for op in self.loopback_result.ops:
            output_log('%s %s %f%%', op.op_in, op.op_out, op.benefit * 100)

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

    def get_benefits(self):
        return self.loopback_result.get_benefits()

    def get_hold_days(self):
        return self.loopback_result.get_hold_days()

    def get_op_dates(self):
        return self.loopback_result.get_op_dates()

    def calc_trend_day_cnt(self, close_ma, volume_ma, volume_ratio):
        cnt = 0
        for idx in reversed(self.df.index):
            row = self.df.loc[idx]
            if row['close'] >= row[close_ma] \
                    and row['volume'] >= row[volume_ma] * volume_ratio \
                    and abs(row['p_change']) < self.MAX_INCR:
                cnt += 1
            else:
                break

        return cnt

    def calc_vol_expand(self):
        today = self.df.shape[0] - 1
        row = self.df.loc[today]
        return row['volume'] / row['V_MA5']

    def break_nday_trend(self, buy_indicator):
        today = self.df.shape[0] - 1
        row = self.df.loc[today]
        return row['close'] >= row[buy_indicator]