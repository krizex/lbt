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

        def add_peak_pair(peak_pairs):
            if peak_pairs:
                peaks.extend(peak_pairs)

        for _, row in self.df.iterrows():
            if filt(row):
                candidates.append(row)
            else:
                if candidates:
                    add_peak_pair(selector(candidates))
                    candidates = []

        if candidates:
            add_peak_pair(selector(candidates))

        return peaks

    def select_peaks(self, l, cmp):
        if len(l) < 3:
            return []

        peaks = []

        prev = l[0]
        cur = l[1]
        for row in l[2:]:
            if cmp(prev['MACD'], cur['MACD']) and cmp(row['MACD'], cur['MACD']):
                peaks.append(cur)

            prev, cur = cur, row

        if len(peaks) < 2:
            return []

        return zip(peaks[:-1], peaks[1:])

    def find_up_peaks(self):
        def filt(row):
            return row['MACD'] > 0.0

        def selector(l):
            return self.select_peaks(l, lambda x, y: x < y)

        return self._find_peaks(filt, selector)

    def find_down_peaks(self):
        def filt(row):
            return row['MACD'] < 0.0

        # get peak pair
        def selector(l):
            return self.select_peaks(l, lambda x, y: x > y)

        return self._find_peaks(filt, selector)

    def _find_inverse(self, peaks, will_inverse, calc_slope):
        inverse_peaks = []
        for prev, cur in peaks:
            if will_inverse(prev['close'], cur['close'], prev[self.index_name], cur[self.index_name]):
                inverse_peaks.append((cur, calc_slope(prev['close'], cur['close'], prev[self.index_name], cur[self.index_name])))

        return inverse_peaks

    def find_top_inverse(self):
        peaks = self.find_up_peaks()

        def will_inverse(close_prev, close_now, macd_prev, macd_now):
            return close_now / close_prev > macd_now / macd_prev

        # TODO: update
        return self._find_inverse(peaks, will_inverse)

    def find_bottom_inverse(self):
        peaks = self.find_down_peaks()

        def will_inverse(close_prev, close_now, macd_prev, macd_now):
            return macd_prev / macd_now > close_now / close_prev

        def calc_slope(close_prev, close_now, macd_prev, macd_now):
            return macd_prev / macd_now

        return self._find_inverse(peaks, will_inverse, calc_slope)
