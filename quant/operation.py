#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Yang Qian'

"""
Created on 06/24/2018
@author: Yang Qian

"""

from abc import abstractmethod, ABCMeta, abstractproperty

class OpBase(object, metaclass=ABCMeta):
    def __init__(self, date, price):
        self.date = date
        self.price = price

    @abstractmethod
    def visit(self, visitor):
        pass

    @abstractmethod
    def __str__(self):
        pass

class OpBuy(OpBase):
    def __init__(self, date, price, cnt):
        super(OpBuy, self).__init__(date, price)
        self.cnt = cnt

    def visit(self, visitor):
        visitor.buy(self)

    def __str__(self):
        return '+ %s %d %s' % (self.date, self.cnt, self.price)


class OpSell(OpBase):
    def __init__(self, date, price, cnt):
        super(OpSell, self).__init__(date, price)
        self.cnt = cnt

    def visit(self, visitor):
        visitor.sell(self)

    def __str__(self):
        return '- %s %d %s' % (self.date, self.cnt, self.price)


class OpStop(OpBase):
    def visit(self, visitor):
        visitor.stop(self)

    def __str__(self):
        return '! %s %s' % (self.date, self.price)
