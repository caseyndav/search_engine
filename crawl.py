#!/usr/bin/env python

import db
import Queue
import threading
import time
import timed_set as ts
from urlparse import urlparse
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
        self.recently_crawled_domains = ts.TimedSet()

    def crawl(self, thread_id, url_queue):
        while not exiting:
            if not url_queue.empty():
                queue_lock.acquire()
                url_str = url_queue.get()
                queue_lock.release()
                parsed_uri = urlparse(url_str)
                domain = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)
                if domain in self.recently_crawled_domains:
                    url_queue.put(url_str)  # If recently crawled, skip for now
                    continue
                content, content_type = self.resolver.resolve_url(url_str)
                page = db.get_page(url_str, pages)
                page.mark_crawled(content, content_type)
                db.update_database(page, pages)
                self.recently_crawled_domains.add(domain)  # Recently crawled

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
