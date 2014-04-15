# -*- coding: utf-8 -*-

""" Text extraction methods.
"""
import re
import urllib2
import logging

import fixpath

from lxml import html, etree
from readability import readability

#------------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class Extractor:

    def __init__(self):
        self._xallnodes = etree.XPath('//*')
        self._shrink_re = re.compile(ur'\s+', flags=re.UNICODE)

    def extract(self, url):

        rawhtml = Extractor._get_raw_html(url)

        # Parse with readability
        doc = readability.Document(rawhtml)

        # Get readable html
        title, html_content = doc.short_title(), doc.summary()

        text_content = self._get_text(html_content)

        # Return JSON object
        return {
            'url'       : url,
            'title'     : doc.short_title(),
            'author'    : None,
            'word_count': -1,
            'content'   : u'<div>{}</div>'.format(text_content),
        }

    @staticmethod
    def _get_raw_html(url):

        urlreq = urllib2.urlopen(url)
        meta   = urlreq.info()

        log.info('Opening mime type "%s"', meta.gettype())

        return urlreq.read()

    def _get_text(self, html_content):

        assert isinstance(html_content, unicode)

        doc = html.fromstring(html_content)

        # Add padding so that text in adjacent tags wouldn't stick
        # together. E.g., "<p>Hello<br/>World!</p>" should look as
        # "Hello World!" and not as "HelloWorld!".
        for node in self._xallnodes(doc):
            if node.tail:
                node.tail = node.tail + ' '
            else:
                node.tail = ' '

        txt = html.tostring( doc, method='text', encoding='unicode')

        txt = self._shrink_re.sub(' ', txt)

        return txt.strip()


# Global extractor instance
extractor = Extractor()

