from .base import Loopback
from quant.stock import Stock
from quant.logger.logger import log
from quant.operation import OpBuy, OpSell, OpStop



class LoopbackTrend(Loopback):
    def __init__(self, persist_f, from_date, to_date, highest_day_n):
        super(LoopbackTrend, self).__init__(persist_f, from_date, to_date, 10, 10)
        self.highest_day_n = highest_day_n
        self.buy_steps = [200, 300, 300, 200]
        self.step_ratio = 0.05
        self.step_exit_ratio = 0.1
        self.stop_ma = 'MA40'
        self.stop_down_ratio_of_ma = 0.03

    def init_internal_result(self):
        super(LoopbackTrend, self).init_inter_result()
        self._past_data = []
        self._cur_hold = 0
        self._start_price = 0.0

    def update_internal_result(self, row):
        if len(self._past_data) >= self.highest_day_n:
            self._past_data = self._past_data[1:]
        self._past_data.append(row)

    def print_loopback_condition(self):
        log.info('>>>>Loopback condition<<<<')
        log.info('trend start from highest in %d days', self.highest_day_n)
        log.info('steps: %s', self.buy_steps)
        log.info('step buy ratio: %.2f%%', self.step_ratio * 100)
        log.info('step exit ratio: %.2f%%', self.step_exit_ratio * 100)
        log.info('stop condition: %.2f%% downside %s', self.stop_down_ratio_of_ma * 100, self.stop_ma)
        log.info('>>>>>>>>>>>>><<<<<<<<<<<<<')

    def where_is_my_chance(self):
        log.info('=====Your chance=====')
        log.info('TBD')

    def plot_benefit(self, title, stocks):
        pass

    def buy(self, row):
        cnt = self.buy_steps[self._cur_hold]
        if self._cur_hold == 0:
            self._start_price = row['close']
        self._cur_hold += 1
        return OpBuy(row['date'], row['close'], cnt)

    def sell(self, row):
        cnt = self.buy_steps[self._cur_hold - 1]
        self._cur_hold -= 1
        return OpSell(row['date'], row['close'], cnt)

    def stop(self, row):
        self._cur_hold = 0
        return OpStop(row['date'], row['close'])

    def is_time_to_buy(self,row):
        price = row['close']
        if self._cur_hold >= len(self.buy_steps):
            return False
        elif self._cur_hold == 0:
            buy_price = self.highest_in_past()
        else:
            buy_price = self._start_price * ((1 + self.step_ratio) ** self._cur_hold)

        if price >= buy_price:
            return True

    def is_time_to_sell(self, row):
        price = row['close']
        if self._cur_hold == 0:
            return False
        else:
            sell_price = self._start_price * ((1 + self.step_ratio) ** (self._cur_hold - 1)) * (1 - self.step_exit_ratio)
            if price <= sell_price:
                return True
            else:
                return False

    def is_time_to_stop(self, row):
        if self._cur_hold == 0:
            return False
        else:
            stop_price = row[self.stop_ma] * (1 - self.stop_down_ratio_of_ma)
            price = row['close']
            if price <= stop_price:
                return True
            else:
                return False

    def highest_in_past(self):
        return max([row['highest'] for row in self._past_data])

    def calc_loopback_result(self):
        return LoopbackTrendResult(self.ops, self.buy_steps, self.step_ratio)
