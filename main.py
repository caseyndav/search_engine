#!/usr/bin/env python

from crawl import *
from index import *


def load_url_frontier():
    return []


def save_url_frontier():
    pass


def main():
    try:
        url_frontier = load_url_frontier()
        crawler = Crawler()
        crawler.populate_queue(url_frontier)
        indexer = Indexer(crawler)
    except KeyboardInterrupt:
        indexer.exit()
        crawler.exit()
