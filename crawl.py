#!/usr/bin/env python

import db
import Queue
import socket
import threading
import time
import urllib2
from url_resolver import URLResolver
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = "27017"

client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)  # Get client
pages = client.dataset.pages  # Get collection "pages"

exiting = 0
queue_lock = threading.Lock()


class CrawlerThread(threading.Thread):

    def __init__(self, thread_id, url_queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.url_queue = url_queue

    def run(self):
        Crawler.crawl(self.thread_id, self.jobs_queue)


class Crawler:

    def __init__(self, url_queue=None):
        if url_queue is None:
            self.url_queue = self.create_queue()
        else:
            self.url_queue = url_queue
        self.threadpool = self.create_threadpool(self.url_queue)
        self.resolver = URLResolver()

    def crawl(self, thread_id, url_queue):
        while not exiting:
            queue_lock.acquire()
            if not url_queue.empty():
                url_str = url_queue.get()
                queue_lock.release()
                content, content_type = self.resolver.resolve_url(url_str)
                page = db.get_page(url_str, pages)
                page.mark_crawled(content, content_type)
                db.update_database(page, pages)
            else:
                queue_lock.release()
            time.sleep(1)

    def create_queue(self, n=100):
        url_queue = Queue.Queue(n)
        return url_queue

    def create_threadpool(self, url_queue, n=100):
        threadpool = []
        for i in xrange(n):
            thread = CrawlerThread(i, url_queue)
            thread.start()
            threadpool.append(thread)
        return threadpool

    def populate_queue(self, url_list):
        queue_lock.acquire()
        for url in url_list:
            self.url_queue.put(url)
        queue_lock.release()

    def exit(self):
        for thread in self.threadpool:
            thread.join()
