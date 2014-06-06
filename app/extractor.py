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
from ebooklib import epub, ITEM_DOCUMENT

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

_PARAG_SEPARATOR = '\n\n'

_TAG_PADDING = {
    'p'     : _PARAG_SEPARATOR,
    'div'   : _PARAG_SEPARATOR,
    'h1'    : _PARAG_SEPARATOR,
    'h2'    : _PARAG_SEPARATOR,
    'h3'    : _PARAG_SEPARATOR,
    'h4'    : _PARAG_SEPARATOR,
}

class CleanDocument:
    """ Readable document fetched from ``source_url``.
    """

    def __init__(self, source_url, url_type=None):
        self.url = source_url
        self.title = None
        self.content = []
        self.author = None
        self.lang = None
        self.direction = None
        self.url_type = url_type
        self._lang = LangGuess()
        self._error = False

    @property
    def source_url(self):
        return self.url

    def is_empty(self):
        return self._error or (not self.content)

    @classmethod
    def from_json(cls, json_object):
        """Create a document instance from JSON dictionary.
        """
        doc = cls(json_object['url'])

        doc._error = json_object.get('error', '').lower() == 'true'

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
            tag = node.tag.lower()

            padding = _TAG_PADDING.get(tag, ' ')

            if node.tail:
                node.tail = node.tail + padding
            else:
                node.tail = padding

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

#------------------------------------------------------------------------------

CONTENT_JSON = 'json'
CONTENT_HTML = 'html'
CONTENT_EPUB = 'epub'
CONTENT_PDF  = 'pdf'

_CONTENT_TYPE_MAP = {
    'application/json'          : CONTENT_JSON,
    'text/html'                 : CONTENT_HTML,
    'application/epub+zip'      : CONTENT_EPUB,
    'application/pdf'           : CONTENT_PDF,
}

#------------------------------------------------------------------------------

class Content:
    """ Representation of content retrieved from URL.
    """

    def __init__(self, url, mime_type, istream):
        self._url = url
        self._type = _CONTENT_TYPE_MAP.get(mime_type)
        if not self._type:
            raise urllib2.HTTPError(url, code=501, # Not Implemented
                    msg='Unsupported mime type: %s' % mime_type,
                    hdrs=None, fp=None)
        self._istream = istream
        self._title = None
        self._author = None

    @property
    def title(self):
        return self._title

    @property
    def type(self):
        return self._type

    @property
    def author(self):
        return self._author

    def to_json(self):
        assert self._type == CONTENT_JSON
        return json.load(self._istream)

    def generate_html_chunks(self):
        assert self._type in [CONTENT_HTML, CONTENT_EPUB]

        if self._type == CONTENT_HTML:
            log.debug('Reading raw HTML from %s', self._url)

            yield self._istream.read()

        elif self._type == CONTENT_EPUB:
            log.debug('Reading ePub from %s', self._url)

            ios = lazygen.BufferedRandomReader(self._istream)
            book = epub.read_epub(ios)

            self._title, self._author = book.title, ''

            authors = book.get_metadata('DC', 'creator')
            if authors:
                self._author = authors[0][0]

            for doc_item in book.get_items_of_type(ITEM_DOCUMENT):
                yield doc_item.content

        elif self._type == CONTENT_PDF:
            yield ''

#------------------------------------------------------------------------------

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
        # Save the round-trip if we're confident ``url`` cannot be parsed
        urll = url.lower()

        if urll.endswith('.epub'):
            url_type = CONTENT_EPUB
        elif urll.endswith('.pdf'):
            url_type = CONTENT_PDF
        else:
            url_type = None

        if url_type:
            log.warn('ePub/pdf CANNOT be parsed with Readability: %s', url)
            return CleanDocument(url, url_type) # empty document fallback

        rdd_args = urllib.urlencode( dict(url=url, token=self._rdd_api_key) )
        rdd_req  = self._rdd_api_url + '?' + rdd_args

        log.info('Getting Readability content from %s', rdd_req)

        try:
            content = Extractor._get_raw_content(rdd_req, 'application/json')

            rdd_doc = CleanDocument.from_json(content.to_json())

        except urllib2.HTTPError as err:
            log.error('Readability error for %s: %d', rdd_req, err.code)

            rdd_doc = CleanDocument(url) # empty document fallback

        # convert html to text
        rdd_doc.textify()

        return rdd_doc

    def _update_content(self, doc):
        """Get readable content using local parser.
        """
        if doc.url_type != CONTENT_PDF:
            content = Extractor._get_raw_content(doc.source_url)
            doc.url_type = content.type

        if doc.url_type == CONTENT_PDF:
            preproc_url = 'http://get-html.appspot.com/q?'
            doc.preprocess = preproc_url + urllib.urlencode( {'u':doc.url} )
            return doc

        word_count, clean, title = 0, [], None

        for rawhtml in content.generate_html_chunks():
            if rawhtml:

                rddoc = readability.Document(rawhtml)

                title = title or rddoc.short_title()

                doc.content = rddoc.summary()

                # convert html to text
                doc.textify()

                clean.append(doc.content)

                word_count += doc.word_count

        doc.title   = content.title or title
        doc.author  = content.author
        doc.content = ''.join(clean)
        doc.word_count = word_count

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

        mime_type = (meta.gettype() or '').lower()

        log.debug('Opening mime type "%s"', mime_type)

        content_type = meta.getheader('content-type', '')
        content_encoding = meta.getheader('content-encoding', '')

        log.debug('Content type: "%s"', content_type)
        log.debug('Content encoding: "%s"', content_encoding)

        # we'll gunzip even if not allowgzip :)
        if content_encoding.lower() in ['gzip', 'deflate']:
            log.debug('Decompressing gzip/deflate response.')

            gunzip_gen = lazygen.gunzip_generator(resp)

            istream = lazygen.StringGenStream(gunzip_gen)

            return Content(url, mime_type, istream)

        return Content(url, mime_type, resp)

# Global extractor instance
extractor = Extractor()

