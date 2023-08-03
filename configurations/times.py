import time
import threading

timeout_thread = None
triggered = False

def sleep(duration, get_now=time.perf_counter):
    """
    Custom sleep function that works more accurate then time.sleep does.
    Taken from: https://stackoverflow.com/a/60185893/3684575
    :param duration: Duration to sleep (in seconds).
    :param get_now: Function to retrieve current time (time.perf_counter by default)
    :return:
    """
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

def start_timeout():
    global timeout_thread, triggered
    if timeout_thread is not None:
        timeout_thread.cancel()
    timeout_thread = threading.Timer(30, stop_listening)
    timeout_thread.start()

def stop_listening():
    global triggered
    triggered = False