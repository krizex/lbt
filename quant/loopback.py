#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from abc import abstractmethod, ABCMeta, abstractproperty
from contextlib import contextmanager
from datetime import datetime, timedelta
from multiprocessing import Pool

import signal
import tushare as ts

from quant.helpers import is_rising_trend
from quant.logger.logger import log
from quant.operation import Op
from quant.peak import Peak
from quant.result import LoopbackResult
from quant.stock import Stock
import cPickle as pickle
import matplotlib.pyplot as plt

__author__ = 'Yang Qian'

"""
Created on 01/31/2018
@author: Yang Qian

"""


def terminate_pool_and_exit(signum, frame):
    global g_pool
    log.warn('Handle signal')
    if g_pool is not None:
        log.info('Closing pool...')
        g_pool.terminate()
        g_pool.join()
    exit(1)


def setup_signal_handler(handler):
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, handler)


def build_stock((idx, (code, info))):
    log.debug('%d Fetching %s %s', idx, code, info['name'].decode('utf8'))
    try:
        stock = Stock(code, info)
        return stock
    except Exception as e:
        log.error('Error fetching %s', code)
        return None


def process_stock(stock):
    try:
        if len(stock.df) == 0:
            return stock

        stock.add_macd()
        stock.add_ma()
        stock.add_vma()
        stock.add_p_change()
    except:
        log.exception('Error occur when processing %s', stock.code)

    return stock


def loopback_stock((loopback, stock)):
    try:
        result = loopback.loopback_one(stock)
        stock.set_loopback_result(result)
    except Exception as e:
        log.exception('Error occur when looping back %s', stock.code)

    return stock


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


def avg(l):
    return sum(l) / 1.0 / len(l)


class LoopInterResult(object):
    def __init__(self):
        self.last_macd = 0.0
        self.last_ma_gap = 0.0


class Loopback(object):
    __metaclass__ = ABCMeta

    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit):
        self.persist_f = self.persiste_f_name(persist_f)
        self.from_date = from_date
        self.to_date = to_date
        self.stop_loss = stop_loss
        self.stop_benefit = stop_benefit
        self.stocks = None
        self.inter_result = LoopInterResult()

    def init(self):
        self.stocks = self.fetch_stocks()

    def persiste_f_name(self, name):
        if name:
            return name
        now = int(time.time())
        time_array = time.localtime(now)
        t = time.strftime("%Y-%m-%d", time_array)
        return 'data/stocks-%s.dat' % t

    def read_stocks_from_persist(self):
        log.info("Read stocks from file:%s", self.persist_f)
        with open(self.persist_f) as f:
            return pickle.load(f)

    def persist_stocks(self, data):
        log.info("Persist stocks to file: %s", self.persist_f)
        with open(self.persist_f, 'w') as f:
            pickle.dump(data, f)

    def fetch_stocks(self):
        if os.path.isfile(self.persist_f):
            stocks = self.read_stocks_from_persist()
        else:
            stocks = self._fetch_stocks()
            self.persist_stocks(stocks)

        log.info('Fetched all stocks')
        return self.process_stocks(stocks)

    def process_stocks(self, stocks):
        with create_pool('process stocks') as pool:
            stocks = pool.map(process_stock, stocks)
        log.info('Processed all stocks')
        return stocks

    def _fetch_stocks(self):
        log.info("Fetch stocks from web")
        stocks = ts.get_stock_basics()
        with create_pool('fetch stocks') as pool:
            ret = pool.map(build_stock, [(i, stock) for i, stock in enumerate(stocks.iterrows())])
            ret = filter(lambda x: x is not None, ret)
            return ret

    def loopback(self):
        # Temporary wipe the stocks in `self` to make the IPC faster
        stocks = self.stocks
        self.stocks = None
        with create_pool('loopback') as pool:
            self.stocks = pool.map(loopback_stock, [(self, stock) for stock in stocks])

    def _select_range(self, df):
        try:
            if self.from_date:
                df = df.loc[df['date'] >= self.from_date]
            if self.to_date:
                df = df.loc[df['date'] <= self.to_date]
        except:
            pass

        return df

    def _set_inter_result(self, row):
        pass

    def _init_inter_result(self):
        pass

    def loopback_one(self, stock):
        df = self._select_range(stock.df)
        hold = False
        in_price = 0.0
        last_price = 0.0
        ops = []
        self._init_inter_result()
        for _, row in df.iterrows():
            last_price = row['close']
            if not hold:
                if self.is_time_to_buy(row):
                    hold = True
                    in_price = row['close']
                    op = Op()
                    op.op_in = '(+) %s' % row['date']
                    ops.append(op)
            else:
                op = ops[-1]
                op.hold_days += 1
                cur_benefit = row['close'] / in_price
                cur_benefit_top = row['high'] / in_price
                cur_benefit_bottom = row['low'] / in_price
                if self.is_time_to_sell(row):
                    hold = False
                    op.op_out = '(-) %s' % row['date']
                    op.benefit = cur_benefit - 1
                elif self.stop_benefit and cur_benefit_top - self.stop_benefit >= 1.0:
                    hold = False
                    op.op_out = '(-^) %s' % row['date']
                    op.benefit = self.stop_benefit
                elif cur_benefit_bottom < 1.0 + self.stop_loss:
                    hold = False
                    op.op_out = '(-V) %s' % row['date']
                    op.benefit = self.stop_loss

            self._set_inter_result(row)

        # assume sell the stock in the last day
        if ops and ops[-1].op_out == '':
            cur_benefit = last_price / in_price
            ops[-1].benefit = cur_benefit - 1

        return LoopbackResult(ops)

    @abstractmethod
    def is_time_to_buy(self, row):
        pass

    @abstractmethod
    def is_time_to_sell(self, row):
        pass

    def plot_benefit(self, title, stocks):
        x = [i for i in range(1, len(stocks) + 1)]
        y = [stock.get_benefit() for stock in stocks]
        plt.plot(x, y, 'ro')
        plt.title(title)
        plt.show()

    def plot_hist(self):
        x = [stock.get_benefit() for stock in self.stocks]
        plt.hist(x)
        plt.xlabel('benefit')
        plt.xlim(-3.0, 3.0)
        plt.ylabel('Frequency')
        plt.title('Benefit hist')
        plt.show()

    def test_loopback_one_by_code(self, code):
        df = ts.get_stock_basics()
        try:
            info = df.loc[code]
        except Exception:
            info = {'name': 'unknown'}
        stock = Stock(code, info)
        self.test_loopback_one(stock)

    def test_loopback_one(self, stock):
        process_stock(stock)
        result = self.loopback_one(stock)
        stock.set_loopback_result(result)
        stock.print_loopback_result()

    @abstractmethod
    def print_loopback_condition(self):
        pass

    def best_stocks(self, filt=None):
        period = 'from %s to %s' % (self.from_date, self.to_date if self.to_date else 'now')
        log.info('Best stocks %s', period)
        log.info('stop benefit: %f%%, stop loss: %f%%', self.stop_benefit * 100, self.stop_loss * 100)
        self.print_loopback_condition()
        if filt:
            self.stocks = filter(filt, self.stocks)
        self.loopback()
        purchased_stocks = self.stocks
        # We only consider the stock we really purchased
        purchased_stocks = filter(lambda x: x.loopback_result is not None and x.loopback_result.ops, purchased_stocks)
        purchased_stocks = sorted(purchased_stocks, key=lambda x: x.loopback_result.benefit, reverse=True)
        benefits = []
        hold_days = []
        stocks = []
        op_dates = []
        for stock in purchased_stocks:
            _benefits = stock.get_benefits()
            if _benefits:
                stock.print_loopback_result(debug=True)
                stocks.append(stock)
                benefits += _benefits
                hold_days += stock.get_hold_days()
                op_dates += stock.get_op_dates()

        math_expt = avg(benefits)
        avg_hold_days = avg(hold_days)
        log.info('Benefit mathematical expectation: %f%% for %d stocks in %d operations, average hold days: %f',
                 math_expt * 100, len(stocks), len(benefits), avg_hold_days)

        self.plot_benefit("%s Math expt: %f" % (period, math_expt), stocks)
        # plot_hist(sorted_stocks)

        self.print_loopback_condition()
        self.print_op_dates(op_dates)
        self.where_is_my_chance()
        return math_expt, len(stocks), len(benefits), avg_hold_days


    @abstractmethod
    def where_is_my_chance(self):
        pass

    def print_op_dates(self, op_dates, skip=True):
        op_d = {}
        for x in op_dates:
            if x in op_d:
                op_d[x] += 1
            else:
                op_d[x] = 1

        x = sorted(op_d.keys())
        y = [op_d[k] for k in x]
        days_cnt = len(x)
        days_2_cnt = len(filter(lambda x: x <= 2, y))
        threashold = 10
        days_more_than_t = len(filter(lambda x: x >= threashold, y))
        log.info('Less than 2 chances: %d days of %d days', days_2_cnt, days_cnt)
        log.info('More than %d chances: %d days of %d days', threashold, days_more_than_t, days_cnt)

        if not skip:
            plt.plot(x, y, 'ro')
            plt.title('Chances per day')
            plt.show()


class LoopbackRSI(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell):
        super(LoopbackRSI, self).__init__(persist_f, from_date, to_date, stop_loss)
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def process_stock(self, stock):
        super(LoopbackRSI, self).process_stock(stock)
        stock.add_rsi(self.rsi_period)

    def is_time_to_buy(self, row):
        return row['RSI'] <= self.rsi_buy

    def is_time_to_sell(self, row):
        return row['RSI'] >= self.rsi_sell

    def print_loopback_condition(self):
        log.info('Loopback condition: rsi_period=%d, rsi_buy=%d, rsi_sell=%d, stop_loss=%f',
                 self.rsi_period, self.rsi_buy, self.rsi_sell, self.stop_loss)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_rsi(self.rsi_buy):
                log.info('%d:', i+1)
                stock.print_loopback_result()

    def plot_pe(self):
        x = [i for i in range(1, len(self.stocks) + 1)]
        y = [stock.pe for stock in self.stocks]
        plt.plot(x, y, 'ro')
        plt.title("pe")
        plt.show()


class LoopbackMACD(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit):
        super(LoopbackMACD, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)

    def is_time_to_buy(self, row):
        return self.inter_result.last_macd <= 0.0 < row['MACD']

    def is_time_to_sell(self, row):
        return row['MACD'] < 0.0

    def _init_inter_result(self):
        self.inter_result.last_macd = 1.0

    def _set_inter_result(self, row):
        self.inter_result.last_macd = row['MACD']

    def print_loopback_condition(self):
        log.info('Loopback condition: MACD')

    def where_is_my_chance(self):
        log.info("=====Your chance=====")
        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_macd():
                log.info('%d:', i+1)
                stock.print_loopback_result()


class LoopbackMACD_RSI(LoopbackMACD, LoopbackRSI):
    def __init__(self, persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell):
        LoopbackRSI.__init__(self, persist_f, from_date, to_date, stop_loss, rsi_period, rsi_buy, rsi_sell)

    def is_time_to_buy(self, row):
        return LoopbackMACD.is_time_to_buy(self, row) and LoopbackRSI.is_time_to_buy(self, row)

    def is_time_to_sell(self, row):
        return LoopbackMACD.is_time_to_sell(self, row) and LoopbackRSI.is_time_to_sell(self, row)

    def _init_inter_result(self):
        LoopbackMACD._init_inter_result(self)
        LoopbackRSI._init_inter_result(self)

    def _set_inter_result(self, row):
        LoopbackMACD._set_inter_result(self, row)
        LoopbackRSI._set_inter_result(self, row)

    def print_loopback_condition(self):
        log.info('RSI-MACD Loopback condition: rsi_period=%d, rsi_buy=%d, rsi_sell=%d, stop_loss=%f',
                 self.rsi_period, self.rsi_buy, self.rsi_sell, self.stop_loss)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_rsi(self.rsi_buy) and stock.is_time_to_buy_by_macd():
                log.info('%d:', i+1)
                stock.print_loopback_result()


class LoopbackMACDRisingTrend(LoopbackMACD):
    def is_time_to_buy(self, row):
        if all([
            is_rising_trend(row),
            row['close'] > row['MA20'],
            LoopbackMACD.is_time_to_buy(self, row),
        ]):
            self.macd_red = False
            return True

        return False

    def is_time_to_sell(self, row):
        if not self.macd_red and row['MACD'] > 0:
            self.macd_red = True
            return False

        if self.macd_red and row['MACD'] < 0:
            return True

        return False

    def print_loopback_condition(self):
        log.info('MACD-MA Loopback condition')

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        for i, stock in enumerate(self.stocks):
            if stock.is_rising_trend_now() and stock.is_time_to_buy_by_macd():
                log.info('%d:', i+1)
                stock.print_loopback_result()


class LoopbackMA(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit, ma_period):
        super(LoopbackMA, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.ma = 'MA%d' % ma_period

    def _init_inter_result(self):
        self.inter_result.last_ma_gap = 1.0

    def _set_inter_result(self, row):
        self.inter_result.last_ma_gap = row['close'] - row[self.ma]

    def is_time_to_buy(self, row):
        cur_gap = row['close'] - row[self.ma]
        return all([
            self.inter_result.last_ma_gap <= 0.0 < cur_gap,
            is_rising_trend(row)
        ])

    def is_time_to_sell(self, row):
        return False

    def print_loopback_condition(self):
        log.info('Loopback condition: MA: %s', self.ma)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")
        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_ma(self.ma):
                log.info('%d:', i+1)
                stock.print_loopback_result()


class LoopbackPeak(Loopback):
    def plot_benefit(self, title, stocks):
        pass

    def print_loopback_condition(self):
        log.info('Loopback condition: inverse')

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        stocks = filter(lambda stock: stock.get_last_op() is not None, self.stocks)

        def get_op_date(stock):
            op = stock.get_last_op()
            return datetime.strptime(op.op_in, '(+) %Y-%m-%d')

        def get_op_slope(stock):
            op = stock.get_last_op()
            return op.slope

        stocks = sorted(stocks, key=get_op_date, reverse=True)
        end_date = get_op_date(stocks[0])
        start_date = end_date - timedelta(days=7)
        stocks = filter(lambda x: start_date <= get_op_date(x) <= end_date, stocks)
        stocks = filter(lambda x: get_op_slope(x) < 0.0, stocks)
        stocks = sorted(stocks, key=get_op_slope)
        for stock in stocks:
            stock.print_loopback_result()

    def is_time_to_sell(self, row):
        pass

    def is_time_to_buy(self, row):
        pass

    def loopback_one(self, stock):
        df = self._select_range(stock.df)
        peaker = Peak(df)
        inverse_points = peaker.find_bottom_inverse()
        ops = []
        for point, slope in inverse_points:
            op = Op()
            op.op_in = '(+) %s' % point['date']
            op.slope = slope
            ops.append(op)

        return LoopbackResult(ops)


class LoopbackBreakresistance(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit, date_range, amplitude):
        super(LoopbackBreakresistance, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.date_range = date_range
        self.amplitude = amplitude
        # internal result
        self._past_data = []
        self._is_data_in_amplitude = False
        self._highest_price = 0.0

    def print_loopback_condition(self):
        log.info('Loopback condition: break resistance in %d days while amplitude is %f%%', self.date_range, self.amplitude * 100)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        for i, stock in enumerate(self.stocks):
            if stock.is_time_to_buy_by_break_resistance(self.date_range, self.amplitude):
                log.info('%d:', i+1)
                stock.print_loopback_result()

    def is_time_to_sell(self, row):
        return row['close'] <= row['MA20']

    def is_time_to_buy(self, row):
        if self._is_data_in_amplitude:
            return row['close'] > self._highest_price and row['close'] > row['MA20']
        else:
            return False

    @staticmethod
    def calc_highest_price(data):
        highests = [x['high'] for x in data]
        return max(highests)

    @staticmethod
    def data_in_amplitude(data, amplitude):
        highest = max([x['high'] for x in data])
        lowest = min([x['low'] for x in data])
        mid = (highest + lowest) / 2.0
        return highest / mid - 1.0 <= amplitude

    def _set_inter_result(self, row):
        if len(self._past_data) >= self.date_range:
            self._past_data = self._past_data[1:]

        self._past_data.append(row)

        if len(self._past_data) >= self.date_range:
            self._highest_price = self.calc_highest_price(self._past_data)
            self._is_data_in_amplitude = self.data_in_amplitude(self._past_data, self.amplitude)


class LoopbackGrid(Loopback):
    def print_loopback_condition(self):
        pass

    def is_time_to_sell(self, row):
        pass

    def is_time_to_buy(self, row):
        pass

    def where_is_my_chance(self):
        pass

    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit, mid, range, size):
        super(LoopbackGrid, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.top = mid * (1.0 + range)
        self.bottom = mid / (1.0 + range)
        self.size = size
        self.ruler = []
        self.cur_hold = 0
        self.mycash = 0.0

    def _init_ruler(self):
        rate = (1.0 * self.top / self.bottom) ** (1.0 / self.size) - 1
        cur = self.bottom / (1.0 + rate)
        for _ in range(self.size + 1):
            cur *= (1.0 + rate)
            self.ruler.append(cur)

        # The ruler is has an additional grid, that means the first buy point is ruler[1]
        self.ruler = self.ruler[::-1]
        log.info('Ruler:')
        for i, r in enumerate(self.ruler):
            log.info('%2d:    %.3f', i, r)

    def buy(self, price, date):
        buy_cnt = 0
        for i in range(self.cur_hold + 2, len(self.ruler)):
            if self.ruler[i] >= price:
                buy_cnt += 1
            else:
                break

        if buy_cnt:
            self.cur_hold += buy_cnt
            self.mycash -= (price * buy_cnt)
            log.info('(+%d) %.2f %s', buy_cnt, price, date)

    def sell(self, price, date):
        sell_cnt = 0
        for i in range(self.cur_hold - 1, -1, -1):
            if price >= self.ruler[i]:
                sell_cnt += 1
            else:
                break

        if sell_cnt:
            self.cur_hold -= sell_cnt
            self.mycash += (price * sell_cnt)
            log.info('(-%d) %.2f %s', sell_cnt, price, date)

    def loopback_one(self, stock):
        self._init_ruler()
        start_money = sum(self.ruler)
        self.mycash = start_money
        df = self._select_range(stock.df)
        last_price = 0.0
        avenues = []
        costs = []
        for _, row in df.iterrows():
            date = row['date']

            # just simulate the fluctuation in one day
            for last_price in [row['open'], row['close']]:
                if self.cur_hold == 0:
                    self.buy(last_price, date)
                elif self.cur_hold == len(self.ruler) - 1:
                    self.sell(last_price, date)
                elif self.ruler[self.cur_hold + 1] >= last_price:
                    self.buy(last_price, date)
                else:
                    self.sell(last_price, date)

            avenue = self.mycash + self.cur_hold * last_price - start_money
            avenues.append(avenue)
            cost = start_money - self.mycash + self.ruler[self.cur_hold]
            costs.append(cost)

        # log.info('cash %.2f, cur_hold %.2f, start_money %.2f', self.mycash, self.cur_hold * last_price, start_money)
        avenue_rate_per_day = []
        for i, avenue in enumerate(avenues):
            avg_cost = sum(costs[:i+1]) / 1.0 / (i + 1)
            avenue_rate_per_day.append(avenue / 1.0 / avg_cost)

        self.plot(avenue_rate_per_day)
        # self.plot(costs)
        # self.plot(avenues)
        log.info('Current hold cnt %d', self.cur_hold)

        return LoopbackResult([], len(avenue_rate_per_day))

    def plot(self, avenue_rate_per_day):
        plt.plot(avenue_rate_per_day)
        plt.ylabel('Avenue rate per day')
        plt.show()


class LoopbackTrend(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit, min_up_day, close_ma, volume_ma, volume_ratio):
        super(LoopbackTrend, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.min_up_day = min_up_day
        # internal result
        self._past_data = []
        self._is_data_in_amplitude = False
        self._highest_price = 0.0
        self.close_ma = close_ma
        self.volume_ma = volume_ma
        self.volume_ratio = volume_ratio

    def _init_inter_result(self):
        self.up_day_cnt = 0

    def print_loopback_condition(self):
        log.info('Loopback condition: %s and %s trend in more than %d days', self.close_ma, self.volume_ma, self.min_up_day)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")
        stocks = []

        for i, stock in enumerate(self.stocks):
            up_days = stock.calc_trend_day_cnt(self.close_ma, self.volume_ma, self.volume_ratio)
            if up_days >= self.min_up_day:
                stocks.append((up_days, stock))

        stocks = sorted(stocks, key=lambda x: x[0], reverse=True)

        for i, (up_days, stock) in enumerate(stocks):
            log.info('%d: up %d days', i+1, up_days)
            stock.print_loopback_result()

    def is_time_to_sell(self, row):
        return False
        # return row['close'] <= row['MA20']

    def is_time_to_buy(self, row):
        if self.up_day_cnt >= self.min_up_day \
                and abs(row['p_change']) <= Stock.MAX_INCR \
                and row['p_change'] < 0.0:
            return True
        else:
            return False

    def _set_inter_result(self, row):
        if row['close'] >= row[self.close_ma] \
                and row['volume'] >= row[self.volume_ma] * self.volume_ratio \
                and abs(row['p_change']) < Stock.MAX_INCR:
            self.up_day_cnt += 1
        else:
            self.up_day_cnt = 0

    def plot_benefit(self, title, stocks):
        pass


class LoopbackPriceVol(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit, vol_expand):
        super(LoopbackPriceVol, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.vol_expand = vol_expand

    def print_loopback_condition(self):
        log.info('Loopback condition: vol expand %f', self.vol_expand)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")
        stocks = []

        for i, stock in enumerate(self.stocks):
            vol_expand = stock.calc_vol_expand()
            if vol_expand >= self.vol_expand:
                stocks.append((vol_expand, stock))

        stocks = sorted(stocks, key=lambda x: x[0], reverse=True)

        for i, (vol_expand, stock) in enumerate(stocks):
            log.info('%d: volume expand %f', i+1, vol_expand)
            stock.print_loopback_result()

    def _init_inter_result(self):
        self.last_row = None
        self.is_time_to_check = False

    def is_time_to_buy(self, row):
        if self.is_time_to_check \
                and row['p_change'] > 0:
            return True

        return False

    def is_time_to_sell(self, row):
        return False

    def _set_inter_result(self, row):
        if self.last_row is not None:
            # volume expands but price not increase much
            if 0.003 <= row['p_change'] <= 0.01 \
                    and (row['volume'] / row['V_MA5']) >= self.vol_expand:
                self.is_time_to_check = True
            else:
                self.is_time_to_check = False

        self.last_row = row

    def plot_benefit(self, title, stocks):
        pass
