#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

__author__ = 'Yang Qian'

"""
Created on 02/01/2018
@author: Yang Qian

"""

root_node = {
    'path': os.path.dirname(__file__)
}

data_node = {
    'path': os.path.join(root_node['path'], 'data')
}

file_store = {
    'path': os.path.join(data_node['path'], 'images')
}

scanner = {
    'interval': 24 * 3600
}

logger = {
    'path': '/var/log',
    'file': 'quant.log',
    'level': logging.DEBUG,
}

handlers = {
    'term': {
        'level': logging.DEBUG
    },
    'file': {
        'level': logging.DEBUG
    }
}
