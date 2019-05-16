from quant.logger.logger import log
import time
import tushare as ts
import json
import os

def fetch_basis():
    log.info('Fetching stock basics...')
    pro = ts.pro_api('4105aca09e41fde2adac11ff8cdf7e05cef205d946e06935562e0010')
    ret = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    log.info('Fetched')
    df = ret[['ts_code', 'name']]
    df = df.set_index('ts_code')
    s = df.to_json(orient='index')
    return json.loads(s)


class __StockBasisMgr(object):
    def __init__(self):
        self.basis = None
        self._init_basis()

    def _init_basis(self):
        for _ in range(10):
            try:
                self.basis = fetch_basis()
                break
            except:
                log.exception('Re-fetch basis')
                time.sleep(10)

    def full_code(self, code):
        if code.startswith('60'):
            return code + '.SH'
        else:
            return code + '.SZ'

    def get_stock_info(self, code):
        code = self.full_code(code)
        return self.basis[code]

    def get_stock_name(self, code):
        return self.get_stock_info(code)['name']


StockBasisMgr = __StockBasisMgr()

