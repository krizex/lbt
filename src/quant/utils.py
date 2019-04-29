#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import signal
import os
from contextlib import contextmanager
from quant.logger.logger import log
from multiprocessing import Pool

__author__ = 'Yang Qian'

"""
Created on 07/07/2018
@author: Yang Qian

"""


def days_between(_from, to):
    d1 = datetime.strptime(_from, '%Y-%m-%d')
    d2 = datetime.strptime(to, '%Y-%m-%d')
    return (d2 - d1).days


def terminate_pool_and_exit(signum, frame):
    global g_pool
    log.warn('Handle signal')
    if g_pool is not None:
        log.info('Closing pool...')
        for p in g_pool._pool:
            os.kill(p.pid, signal.SIGKILL)
        # .is_alive() will reap dead process
        while any(p.is_alive() for p in g_pool._pool):
            pass
        g_pool.terminate()
        g_pool.join()
    exit(1)


def setup_signal_handler(handler):
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, handler)


g_pool = None
@contextmanager
def create_pool(target):
    global g_pool
    if g_pool is None:
        setup_signal_handler(signal.SIG_IGN)
        log.debug('Create pool')
        g_pool = Pool(4)
        setup_signal_handler(terminate_pool_and_exit)

    log.debug('Enter pool: %s', target)
    start = datetime.now()
    yield g_pool
    cost = datetime.now() - start
    log.debug('Exit pool: %s, takes %d seconds', target, cost.total_seconds())
