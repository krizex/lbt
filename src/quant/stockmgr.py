import time
import os
import tushare as ts
from quant.logger.logger import log
import pickle as pickle
from quant.utils import create_pool
from quant.stock import Stock
from quant.singleton import Singleton


def build_stock(stock_info):
    (idx, (code, info)) = stock_info
    log.debug('%d Fetching %s %s', idx, code, info['name'])
    for _ in range(5):
        try:
            stock = Stock(code, info)
            return stock
        except Exception as e:
            log.error('Error fetching %s, retrying...', code)
            time.sleep(3)
    return None


def process_stock(stock):
    try:
        if len(stock.df) == 0:
            return stock

        stock.process()
    except:
        log.exception('Error occur when processing %s', stock.code)

    return stock


class StockMgr(metaclass=Singleton):
    def __init__(self, persist_f):
        self.persist_f = self.persiste_f_name(persist_f)
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
        with open(self.persist_f, 'rb') as f:
            return pickle.load(f)

    def persist_stocks(self, data):
        log.info("Persist stocks to file: %s", self.persist_f)
        os.makedirs(os.path.dirname(self.persist_f), exist_ok=True)
        with open(self.persist_f, 'wb') as f:
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
            ret = [x for x in ret if x is not None]
            return ret
