import threading
import time
from quant import dummy_web_server
from quant.trend import find_chances
from quant.server.chances import _write_chances
from quant.logger.logger import log


class WebServerThread(threading.Thread):
    def run(self):
        dummy_web_server.run(port=8000)


def main():
    web_t = WebServerThread()
    web_t.start()

    d_from = '2016-01-01'
    while True:
        try:
            start = time.time()
            stocks = find_chances(d_from, None, 22)
            end = time.time()
            write_chances(stocks, end - start)
        except KeyboardInterrupt:
            raise
        except:
            log.exception('Fail to write chances')


if __name__ == '__main__':
    main()
