#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 02/07/2018
@author: Yang Qian

"""


class Peak(object):
    def __init__(self, df):
        self.df = df
        self.index_name = 'MACD'

    def _find_peaks(self, filt, selector):
        peaks = []
        candidates = []
        for _, row in self.df.iterrows():
            if filt(row):
                candidates.append(row)
            else:
                if candidates:
                    peaks.append(selector(candidates))
                    candidates = []

        if candidates:
            peaks.append(selector(candidates))

        return peaks

    def find_up_peaks(self):
        def filt(row):
            return row['MACD'] > 0.0

        def selector(l):
            return max(l, key=lambda row: row['MACD'])

        return self._find_peaks(filt, selector)

    def find_down_peaks(self):
        def filt(row):
            return row['MACD'] < 0.0

        def selector(l):
            return min(l, key=lambda row: row['MACD'])

        return self._find_peaks(filt, selector)

    def _find_inverse(self, peaks, will_inverse):
        inverse_peaks = []
        prev = peaks[0]
        for row in peaks[1:]:
            if will_inverse(prev['close'], row['close'], prev[self.index_name], row[self.index_name]):
                inverse_peaks.append(row)

            prev = row

        return inverse_peaks

    def find_top_inverse(self):
        peaks = self.find_up_peaks()

        def will_inverse(close_prev, close_now, macd_prev, macd_now):
            return close_now / close_prev > macd_now / macd_prev

        return self._find_inverse(peaks, will_inverse)

    def find_bottom_inverse(self):
        peaks = self.find_down_peaks()

        def will_inverse(close_prev, close_now, macd_prev, macd_now):
            return macd_prev / macd_now > close_now / close_prev

        return self._find_inverse(peaks, will_inverse)
