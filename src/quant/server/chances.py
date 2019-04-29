import threading
import time

lock = threading.Lock()
g_chances = None

def write_chances(stocks):
    chances = []
    for stock in stocks:
        benefit, ops = stock.get_loopback_result()
        chances.append((stock.code, stock.name, benefit, ops))

    _write_chances(chances)


def _write_chances(chances):
    global g_chances
    with lock:
        now = int(time.time())
        time_array = time.localtime(now)
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        g_chances = {
            'timestamp': cur_time,
            'data': chances,
        }


def read_chances():
    global g_chances
    with lock:
        return g_chances
