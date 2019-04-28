#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tushare as ts

__author__ = 'Yang Qian'

"""
Created on 02/22/2018
@author: Yang Qian

"""


def not_startup(stock):
    """Not in startup board"""
    return not (stock.code.startswith('300'))

def pe_less_than(pe):
    return lambda stock: stock.pe < pe


def not_startup_and_pe_less_than(pe):
    return lambda x: not_startup(x) and pe_less_than(pe)(x)


def get_codes(df):
    codes = []
    for x in df.iterrows():
        codes.append(x[1]['code'])

    return codes


def is_in_hs300():
    codes = get_codes(ts.get_hs300s())

    def _aux(stock):
        """Stock in HS300"""
        return stock.code in codes

    return _aux


def is_in_sz50():
    codes = get_codes(ts.get_sz50s())

    def _aux(stock):
        """Stock in SZ50"""
        return stock.code in codes

    return _aux


def is_in_zz500():
    codes = get_codes(ts.get_zz500s())

    def _aux(stock):
        """Stock in ZZ500"""
        return stock.code in codes

    return _aux
