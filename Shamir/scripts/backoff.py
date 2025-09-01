# --- backoff.py ---
import time

def backoff_delays(base=1.5, start=1.0, cap=30.0):
    delay = start
    while True:
        yield min(delay, cap)
        delay *= base

def retry_loop(do_try, should_stop=lambda: False, base=1.5, start=1.0, cap=30.0):
    for d in backoff_delays(base, start, cap):
        ok = do_try()
        if ok or should_stop():
            return ok
        time.sleep(d)
