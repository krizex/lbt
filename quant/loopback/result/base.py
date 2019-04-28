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


class Result(object):
    __metaclass__ = ABCMeta

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
        for op in self.ops:
            op.visit(self)

        return sum([benefit for _, benefit in self.benefit])

    def print_ops(self, logger):
        for op in self.ops:
            logger('%s', op)
