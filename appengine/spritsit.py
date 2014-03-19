
import fixpath

import webapp2
import urllib
import logging
from readability import readability
from readability.readability import Document

import lxml.html
import re
import json

MAGIC = '112358'

class BaseHandler(webapp2.RequestHandler):

    def _create_document(self):

        if self.request.get('m') != MAGIC:
            logging.exception('Magic is not valid')
            webapp2.abort(403) # forbidden

        uri = self.request.get('u')

        if not uri:
            logging.exception('URI parameter is not found in request')
            webapp2.abort(400) # bad request

        # Read raw html
        rawhtml = urllib.urlopen(uri).read()

        # Parse with readability
        doc = Document(rawhtml)

        # Get readable html
        html = doc.summary()

        # Reformat as plain text
        txt = lxml.html.tostring(lxml.html.fromstring(html), method='text', encoding='utf-8')
        txt = txt.strip()
        txt = re.sub(r'\s+', r' ', txt, flags=re.MULTILINE)
        txt = re.sub(r'\)\.', r'). ', txt, flags=re.MULTILINE)

        # Create JSON object
        return dict(uri=uri, title=doc.short_title(), content=txt)


class TextHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'

        doc = self._create_document()

        self.response.write(
            '{title}\n\n{uri}\n\n{content}\n\n'.format(**doc))

class JsonHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = 'http://s.codepen.io'

        json.dump(self._create_document(), self.response)


application = webapp2.WSGIApplication([

    (r'/text', TextHandler),
    (r'/json', JsonHandler),

], debug=True)

