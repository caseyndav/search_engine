#!/usr/bin/env python

import threading
import time


def remove_after_interval(my_set, item, interval=1):
    time.sleep(interval)
    my_set.remove(item)

class TimedSet(set):
    def add(self, item):
        set.add(self, item)
        t = threading.Thread(target=remove_after_interval, args=(self, item))
        t.start()
        t.join()