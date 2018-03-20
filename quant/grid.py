#!/usr/bin/env python
# -*- coding: utf-8 -*-
from quant.loopback import LoopbackGrid

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def test_one_stock_grid(code, from_date, to_date, mid, range, size):
    loopback = LoopbackGrid(None, from_date, to_date, None, None, mid, range, size)
    loopback.test_loopback_one_by_code(code)


if __name__ == '__main__':
    d_2016 = '2016-08-16'
    d_2017 = '2017-08-16'
    # test_one_stock_grid('159922', d_2017, d_2018, 6.5, 0.3, 20)
    # test_one_stock_grid('512000', d_2017, d_2018, 1.038, 0.3, 30)
    # test_one_stock_grid('162411', '2017-04-10', '2018-01-22', 0.567, 0.3, 20)
    # test_one_stock_grid('510110', '2016-04-06', '2017-04-25', 3.0, 0.5, 20)
    # test_one_stock_grid('159922', '2016-05-11', d_2017, 6.3, 0.3, 20)
    # test_one_stock_grid('601601', '2017-11-30', '2018-02-26', 40, 0.25, 10)
    # test_one_stock_grid('002415', '2017-11-30', '2018-02-27', 40, 0.25, 10)
    # test_one_stock_grid('512000', '2017-09-04', '2018-03-12', 0.911, 0.10, 20)
    # test_one_stock_grid('159929', '2017-09-04', '2018-02-27', 1.556, 0.10, 20)
    test_one_stock_grid('159949', '2017-09-04', '2018-02-27', 0.695, 0.10, 20)

    # test_one_stock_grid('512000', '2017-09-04', '2018-03-12', 0.880, 0.104, 20)
    # test_one_stock_grid('600036', '2018-02-08', '2018-03-12', 30.0, 0.10, 10)
    # test_one_stock_grid('601318', '2017-11-29', '2018-03-12', 68.0, 0.10, 10)
    # test_one_stock_grid('601601', '2017-11-29', '2018-03-12', 40.0, 0.10, 10)
    # test_one_stock_grid('600507', '2017-11-29', '2018-03-12', 15.7, 0.10, 10)
    # test_one_stock_grid('600506', '2017-11-09', '2018-01-16', 15.04, 0.10, 10)
    # test_one_stock_grid('159915', '2017-08-07', '2018-03-12', 1.605, 0.15, 20)




