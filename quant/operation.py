#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 06/24/2018
@author: Yang Qian

"""


class Op(object):
    def __init__(self):
        self.op_in = ''
        self.op_out = ''
        self.benefit = 0.0
        self.slope = 0.0
        self.hold_days = 0