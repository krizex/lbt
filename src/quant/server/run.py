import threading
import gc
import time
import datetime
from quant import dummy_web_server
from quant.trend import find_chances
from quant.server.chances import write_chances
from quant.logger.logger import log


class WebServerThread(threading.Thread):
    def run(self):
        dummy_web_server.run(port=8000)


def is_time_to_run(prev, now, expt):
    return prev <= expt <= now


def main():
    web_t = WebServerThread()
    web_t.start()

    d_from = '2016-01-01'

    prev_check = datetime.datetime.now()
    while True:
        gc.collect()
        expect = datetime.datetime(prev_check.year, prev_check.month, prev_check.day, hour=15, minute=30, second=0)
        now_check = datetime.datetime.now()
        if is_time_to_run(prev_check, now_check, expect):
            try:
                start = time.time()
                stocks = find_chances(d_from, None, 22)
                end = time.time()
                write_chances(stocks, end - start)
            except KeyboardInterrupt:
                raise
            except:
                log.exception('Fail to write chances')
        else:
            time.sleep(60)

        prev_check = now_check


if __name__ == '__main__':
    main()
