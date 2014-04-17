# -*- coding: utf-8 -*-

""" Text extraction methods.
"""
import re
import json
import urllib
import urllib2
import logging

import lazygen
from settings import settings

import fixpath

from lxml import html, etree
from readability import readability

#------------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class CleanDocument:
    """ Readable document fetched from `source_url`.
    """

    def __init__(self, source_url, title=None, content=None, author=None):
        self.url = source_url
        self.title = title
        self.content = content
        self.author = author

    @property
    def source_url(self):
        return self.url

    def is_empty(self):
        return (not self.content)

    @classmethod
    def from_json(cls, json_object):
        """Create a document instance from JSON dictionary.
        """
        doc = cls(json_object['url'])

        for key, value in json_object.iteritems():
            setattr(doc, key, value)

        return doc

    def json_generator(self):
        """Return generator that produces JSON strings.
        """
        json_object = dict((k, v) for (k, v) in self.__dict__.iteritems())

        return lazygen.json_generator(json_object)


class Extractor:

    def __init__(self):
        self._xallnodes = etree.XPath('//*')
        self._shrink_re = re.compile(ur'\s+', flags=re.UNICODE)

        # Params for working with Readability APIs
        rdd_parser = settings.parsers['Readability']

        self._rdd_api_url = rdd_parser['uri']
        self._rdd_api_key = rdd_parser['token']

    def extract(self, url):

        # Try getting Readability content first
        doc = self._get_from_rdd(url)

        # Parse locally if Readability content is empty
        if doc.is_empty():
            log.warn('Readability content is empty, running local parser.')
            self._update_content(doc)
        else:
            log.info('Returning Readability content.')

        return doc

    def _get_from_rdd(self, url):
        """Use Readability online API.
        """
        rdd_args = urllib.urlencode( dict(url=url, token=self._rdd_api_key) )
        rdd_req  = self._rdd_api_url + '?' + rdd_args

        rdd_json = Extractor._get_raw_content(rdd_req, 'application/json')
        rdd_doc  = CleanDocument.from_json(json.load(rdd_json))

        return rdd_doc

    def _update_content(self, doc):
        """Get readable content using local parser.
        """
        rawhtml = Extractor._get_raw_content(doc.source_url).read()

        rddoc = readability.Document(rawhtml)

        title, html_content = rddoc.short_title(), rddoc.summary()

        text_content = self._get_text(html_content)

        doc.title = doc.title or title
        doc.word_count = float('NaN')
        doc.content = u'<div>{}</div>'.format(text_content)


    @staticmethod
    def _get_raw_content(url, mime=None, allowgzip=True):
        """ Get data from given url.

        Return file-like object so it can be fed to json.load()
        """

        req = urllib2.Request(url)

        if mime:
            req.add_header('Accept', mime)

        if allowgzip:
            req.add_header('Accept-Encoding', 'gzip,deflate')

        resp = urllib2.urlopen(req)

        meta = resp.info()

        mime_type = meta.gettype()

        log.debug('Opening mime type "%s"', mime_type)

        content_type = meta.getheader('content-type', '')
        content_encoding = meta.getheader('content-encoding', '')

        log.debug('Content type: "%s"', content_type)
        log.debug('Content encoding: "%s"', content_encoding)

        # we'll gunzip even if not allowgzip :)
        if content_encoding.lower() in ['gzip', 'deflate']:
            log.debug('Decompressing gzip/deflate response.')

            gunzip_gen = lazygen.gunzip_generator(resp)

            return lazygen.StringGenStream(gunzip_gen)

        return resp

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

