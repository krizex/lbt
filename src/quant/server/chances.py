import threading
import time

lock = threading.Lock()
g_chances = {
    'timestamp': 'NOT STARTED'
}

def write_chances(stocks, underestimate_stocks, duration):
    chances = []
    for stock in stocks:
        benefit, ops = stock.get_loopback_result()
        chances.append((stock.code, stock.name, benefit, ops))

    underestimate_chances = []
    for pos, stock in underestimate_stocks:
        underestimate_chances.append((stock.code, stock.name, pos))

    _write_chances(chances, underestimate_chances, duration)


def _write_chances(chances, underestimate_chances, duration):
    global g_chances
    with lock:
        now = int(time.time())
        time_array = time.localtime(now)
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        g_chances = {
            'timestamp': cur_time,
            'duration': duration,
            'data': chances,
            'underestimate_chances': underestimate_chances,
        }


def read_chances():
    global g_chances
    with lock:
        return g_chances
