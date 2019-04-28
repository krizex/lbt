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


class LoopbackBreak(Loopback):
    def __init__(self, persist_f, from_date, to_date, stop_loss, stop_benefit):
        super(LoopbackBreak, self).__init__(persist_f, from_date, to_date, stop_loss, stop_benefit)
        self.buy_indicator = 'MAX_%d' % 22
        self.sell_indicator = 'MIN_%d' % 11

    def print_loopback_condition(self):
        log.info('Loopback condition: break trend: buy: %s, sell: %s', self.buy_indicator, self.sell_indicator)

    def where_is_my_chance(self):
        log.info("=====Your chance=====")

        stocks = filter(lambda stock: stock.break_nday_trend(self.buy_indicator), self.stocks)
        stocks = sorted(stocks, key=lambda stock: stock.get_benefit(), reverse=True)
        for stock in stocks:
            stock.print_loopback_result()

    def is_time_to_sell(self, row):
        return row['close'] < row[self.sell_indicator]

    def is_time_to_buy(self, row):
        return row['close'] >= row[self.buy_indicator]

    def plot_benefit(self, title, stocks):
        pass
