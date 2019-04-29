#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 06/24/2018
@author: Yang Qian

"""

from abc import abstractmethod, ABCMeta, abstractproperty
from collections import namedtuple


Unit = namedtuple('Unit', ['price', 'cnt'])


class Result(object, metaclass=ABCMeta):
    def __init__(self, ops):
        self.cur_hold = []
        self.benefit = []
        self.ops = ops

    def add_benefit_rate(self, date, benefit):
        self.benefit.append((date, benefit))

    @abstractmethod
    def buy(self, op):
        pass

    @abstractmethod
    def sell(self, op):
        pass

    @abstractmethod
    def stop(self, op):
        pass

    def calc_benefit_rate(self):
        self.benefit = []
        for op in self.ops:
            op.visit(self)

        return sum([benefit for _, benefit in self.benefit])

    def str_of_ops(self):
        ret = []
        for op in self.ops:
            benefit = self._find_benefit(op.date)
            if benefit is not None:
                ret.append('%s -> %+.2f%%' % (op, benefit * 100))
            else:
                ret.append('%s' % op)

        return ret


    def _find_benefit(self, date):
        for b in self.benefit:
            if b[0] == date:
                return b[1]

        return None
