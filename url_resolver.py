#!/usr/bin/env python

import urllib2


class URLResolver:

    # May need to add code to check if this is an anchor pointing to the same
    # page, or some malformed URL that doesn't give a proper error, like a news
    # website that links back to its homepage if an article isn't found at the
    # URL, etc.
    def resolve_url(self, url_str):
        content, content_type = None, None
        try:
            response = urllib2.urlopen(url_str)
            content = response.read()
            content_type = response.headers.gettype()
        except:
            pass
        return content, content_type
