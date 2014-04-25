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

import pyphen
from guess_language import guessLanguage

#------------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

_regex = {
    'paragraphs': re.compile(ur'\n\s*\n\s*|\n\s\s+', flags=re.UNICODE),
    'spaces': re.compile(ur'\s+', flags=re.UNICODE),
    'longdash': re.compile(ur'\-{2,}', flags=re.UNICODE),
}

XPATH_ALL_NODES = etree.XPath('//*')

#------------------------------------------------------------------------------

class CleanDocument:
    """ Readable document fetched from `source_url`.
    """

    def __init__(self, source_url, title=None, content=None, author=None):
        self.url = source_url
        self.title = title
        self.content = content
        self.author = author
        self._pyphen = None

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
        json_object = dict((k, v) for (k, v) in self.__dict__.iteritems()
                if not k.startswith('_'))

        return lazygen.json_generator(json_object)

    def textify(self):
        """ Transform html content to plain text.
        """
        if not self.content:
            return

        assert isinstance(self.content, unicode)

        doc = html.fromstring(self.content)

        # Add padding so that text in adjacent tags wouldn't stick
        # together. E.g., "<p>Hello<br/>World!</p>" should look as
        # "Hello World!" and not as "HelloWorld!".
        for node in XPATH_ALL_NODES(doc):
            if node.tail:
                node.tail = node.tail + ' '
            else:
                node.tail = ' '

        txt = html.tostring(doc, method='text', encoding='unicode')

        # Little cleanup surgery
        paragraphs = _regex['paragraphs'].split(txt)
        pcleaned = []

        for parag in paragraphs:
            words   = _regex['spaces'].split(parag)
            wclean  = []

            for word in words:
                if word: # it must have been stripped by split()
                    wclean.extend(self._clean_word(word, parag))

            pcleaned.append(' '.join(wclean))

        self.content = '\n'.join(pcleaned)

    def _clean_word(self, word, wordcorpus):
        outlist = []

        dash_separated = _regex['longdash'].split(word)

        if len(dash_separated) >= 2:
            for subword in dash_separated:
                outlist.extend(self._clean_word(subword, wordcorpus))
                outlist.append(u'\u2014') # mdash
            return outlist[:-1]

        if len(word) <= settings.max_word_len:
            return [word]
        else:
            if not self._pyphen:
                lang = guessLanguage(wordcorpus)

                log.info('Language guessed: %s', lang)

                if lang == 'UNKNOWN': lang = 'en' # fallback

                self._pyphen = pyphen.Pyphen(lang=lang)

            return [self._pyphen.multiwrap(word, settings.max_word_len)]

class Extractor:

    def __init__(self):

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

        log.info('Getting Readability content from %s', rdd_req)

        rdd_json = Extractor._get_raw_content(rdd_req, 'application/json')
        rdd_doc  = CleanDocument.from_json(json.load(rdd_json))

        # convert html to text
        rdd_doc.textify()

        return rdd_doc

    def _update_content(self, doc):
        """Get readable content using local parser.
        """
        rawhtml = Extractor._get_raw_content(doc.source_url).read()

        rddoc = readability.Document(rawhtml)

        title, html_content = rddoc.short_title(), rddoc.summary()

        doc.title = doc.title or title
        doc.word_count = float('NaN')
        doc.content = html_content

        # convert html to text
        doc.textify()

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

# Global extractor instance
extractor = Extractor()

