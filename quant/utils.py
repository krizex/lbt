#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'Yang Qian'

"""
Created on 07/07/2018
@author: Yang Qian

"""


def days_between(_from, to):
    d1 = datetime.strptime(_from, '%Y-%m-%d')
    d2 = datetime.strptime(to, '%Y-%m-%d')
    return (d2 - d1).days