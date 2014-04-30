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
from guess_language import guess_language

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

LANG_FALLBACK = 'en'
LANG_UNKNOWN  = guess_language.UNKNOWN
HYPH_FALLBACK = pyphen.Pyphen(lang=LANG_FALLBACK)

class LangGuess:
    """ Try guessing document language with ``guess_language``.
    """

    def __init__(self):
        self._lang   = None
        self._corpus = None
        self._wcount = 0
        self._pyphen = None

    def get_lang(self):

        lang = self._guess_lang()

        return lang if lang else LANG_FALLBACK

    def update_corpus(self, words, wordcount):

        if (wordcount > self._wcount) and (wordcount <= 256 or
               self._wcount <= 3):
            self._corpus, self._wcount = words, wordcount

    def _guess_lang(self, wordcontext=None):

        if not self._lang:
            words = self._corpus

            if not words:
                words = wordcontext

            lang = guess_language.guessLanguage(words)

            log.info('Guessed lang: %s', lang)

            if self._lang == LANG_UNKNOWN:
                lang = None

            self._lang = lang

        return self._lang

    def get_hyphenator(self, wordcontext):

        if self._pyphen:
            return self._pyphen

        try:
            lang = self._guess_lang(wordcontext)

            self._pyphen = pyphen.Pyphen(lang=lang)

            return self._pyphen

        except Exception as err:
            log.error("Couldn't create hyphenator for %r: %r", lang, err)

        return HYPH_FALLBACK

#------------------------------------------------------------------------------

class CleanDocument:
    """ Readable document fetched from ``source_url``.
    """

    def __init__(self, source_url, title=None, content=None, author=None):
        self.url = source_url
        self.title = title
        self.content = content
        self.author = author
        self.lang = None
        self.direction = None
        self._lang = LangGuess()

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
        pcleaned, word_count = [], 0

        for parag in paragraphs:
            words   = _regex['spaces'].split(parag)
            wclean  = []

            for word in words:
                if word: # it must have been stripped by split()
                    wclean.extend(self._clean_word(word, parag))

            parag_len = len(wclean)

            word_count += parag_len

            self._lang.update_corpus(parag, parag_len)

            pcleaned.append(' '.join(wclean))

        self.content = '\n'.join(pcleaned)
        self.lang = self._lang.get_lang()
        self.word_count = word_count

        if self.lang in ['he', 'ar']:
            self.direction = 'rtl'
        elif not self.direction:
            self.direction = 'ltr'

    def _clean_word(self, word, wordcontext):
        outlist = []

        dash_separated = _regex['longdash'].split(word)

        if len(dash_separated) >= 2:
            for subword in dash_separated:
                outlist.extend(self._clean_word(subword, wordcontext))
                outlist.append(u'\u2014') # mdash
            return outlist[:-1]

        if len(word) <= settings.max_word_len:
            return [word]
        else:
            hyphenator = self._lang.get_hyphenator(wordcontext)
            return [hyphenator.multiwrap(word, settings.max_word_len)]

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

