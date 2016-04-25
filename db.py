#!/usr/bin/env python

import datetime


class Page:

    def __init__(self, url_string):
        self._id = url_string
        self.content = ""
        self.content_type = ""
        self.token_list = []
        self.anchors = []
        self.time_crawled = None
        self.time_indexed = None

    def mark_crawled(self, content, content_type):
        self.content = content
        self.content_type = content_type
        self.time_crawled = datetime.datetime.utcnow()

    def mark_indexed(self, token_list, anchors):
        self.token_list = token_list
        self.anchors = anchors
        self.time_indexed = datetime.datetime.utcnow()


def update_database(page, collection):
    collection.update_one({"_id": page._id},
                          {
                            "$set": {
                                "content": page.content,
                                "content_type": page.content_type,
                                "token_list": page.token_list,
                                "anchors": page.anchors,
                                "time_crawled": page.time_crawled,
                                "time_indexed": page.time_indexed
                            }
                          })


def get_page(id, collection):
    page = Page(id)
    cursor = collection.find({"_id": id})
    if cursor.count() > 0:
        document = cursor[0]
        page.content = document["content"]
        page.content_type = document["content_type"]
        page.token_list = document["token_list"]
        page.anchors = document["anchors"]
        page.time_crawled = document["time_crawled"]
        page.time_indexed = document["time_indexed"]
    return page
