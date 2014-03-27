import os
import re
import json

import webapp2
import urllib
import logging

import fixpath

from readability import readability
from readability.readability import Document

import lxml.html as lhtml

# Dumb authorization for now
READ_API_TOKEN = os.environ['READ_API_TOKEN']

class BaseHandler(webapp2.RequestHandler):

    def _create_document(self):

        req_token = self.request.get('token')

        if req_token != READ_API_TOKEN:
            logging.error('TOKEN field is not valid: \'{}\' is not {}',
                req_token, READ_API_TOKEN)
            webapp2.abort(403) # forbidden

        url = self.request.get('url')

        if not url:
            logging.error('URL parameter is not found in request')
            webapp2.abort(400) # bad request

        # Read raw html
        rawhtml = urllib.urlopen(url).read()

        # Parse with readability
        doc = Document(rawhtml)

        # Get readable html
        html = doc.summary()

        # Reformat as plain text
        txt = lhtml.tostring(lhtml.fromstring(html), method='text', encoding='utf-8')

        txt = txt.strip()
        txt = re.sub(r'\s+', r' ', txt, flags=re.MULTILINE)
        txt = re.sub(r'\)\.', r'). ', txt, flags=re.MULTILINE)

        # Create JSON object
        return {
            'url'       : url,
            'title'     : doc.short_title(),
            'content'   : txt,
        }


class TextHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'

        doc = self._create_document()

        for field in ['title', 'content']: # 'url'
            value = doc[field]

            logging.debug('Writing field {} of {}'.format(
                field, type(value)))

            self.response.write(value)

            self.response.write('\n\n')

class JsonHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'

        # FIXME: Be more specific in CORS; but for now rely on 'token'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        json.dump(self._create_document(), self.response)


application = webapp2.WSGIApplication([

    (r'/text', TextHandler),
    (r'/json', JsonHandler),

], debug=True)

