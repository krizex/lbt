import threading
import time
from quant import dummy_web_server
from quant.trend import find_chances
from quant.server.chances import write_chances


class WebServerThread(threading.Thread):
    def run(self):
        dummy_web_server.run(port=8000)


def main():
    web_t = WebServerThread()
    web_t.start()

    d_from = '2016-01-01'
    while True:
        now = int(time.time())
        time_array = time.localtime(now)
        d_to = time.strftime("%Y-%m-%d", time_array)
        stocks = find_chances(d_from, d_to, 22)
        write_chances(stockks)


if __name__ == '__main__':
    main()
