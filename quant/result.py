#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 06/24/2018
@author: Yang Qian

"""

class LoopbackResult(object):
    def __init__(self, ops, hold_days=0):
        self._benefit = None
        self.ops = ops
        self.hold_days = hold_days

    @property
    def benefit(self):
        if self._benefit is not None:
            return self._benefit
        else:
            benefits = [op.benefit + 1 for op in self.ops]
            benefit = reduce(lambda x, y: x * y, benefits, 1.0) - 1.0
            self._benefit = benefit
            return self._benefit

    def get_benefits(self):
        return [op.benefit for op in self.ops]

    def get_hold_days(self):
        return [op.hold_days for op in self.ops]

    def get_op_dates(self):
        return [op.op_in.split(')')[1].strip() for op in self.ops]