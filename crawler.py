#!/usr/bin/env python

import Queue
import sys
import threading
import time


exiting = 0
queue_lock = threading.Lock()


class CrawlerThread(threading.Thread):

    def __init__(self, thread_id, jobs_queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.jobs_queue = jobs_queue

    def run(self):
        crawl(self.thread_id, self.jobs_queue)


def crawl(thread_id, jobs_queue):
    while not exiting:
        queue_lock.acquire()
        if not jobs_queue.empty():
            job = jobs_queue.get()
            queue_lock.release()
            print "Thread %d is now processing %s" % (thread_id, job)
        else:
            queue_lock.release()
        time.sleep(1)


def create_queue(n=100):
    jobs_queue = Queue.Queue(n)
    return jobs_queue


def create_threadpool(jobs_queue, n=100):
    threadpool = []
    for i in xrange(n):
        thread = CrawlerThread(i, jobs_queue)
        thread.start()
        threadpool.append(thread)
    return threadpool


def populate_queue(jobs_queue):
    queue_lock.acquire()
    jobs_list = ["job0", "job1", "job2", "job3", "job4"]
    for job in jobs_list:
        jobs_queue.put(job)
    queue_lock.release()


def main():
    jobs_queue = create_queue()
    populate_queue(jobs_queue)
    threadpool = create_threadpool(jobs_queue)
    while True:
        if exiting == 1:
            for thread in threadpool:
                thread.join()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exiting = 1
