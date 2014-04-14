# -*- coding: utf-8 -*-
import re
import urllib2
import StringIO

from os import environ
import logging as _logging

from types import GeneratorType
from lazygen import json_generator, flat_string_generator

import fixpath

from flask import Flask, abort, Response
from readability import readability
from lxml import html as lhtml

#-----------------------------------------------------------------------------

# Dumb authorization for now (mandatory)
READ_API_TOKEN = environ['READ_API_TOKEN']

# Google App Engine disallows dynamically built responses because it
# wants to know the response content length upfront :(
ALLOW_STREAMING = environ.get('ALLOW_STREAMING', '1')

# Current app version (mandatory)
CURRENT_VERSION_ID = environ['CURRENT_VERSION_ID']

# Verbosity level
APP_DEBUG = environ.get('APP_DEBUG', '0')

#-----------------------------------------------------------------------------

# App logger
log = _logging.getLogger(__name__)

# Cast to boolean value
ALLOW_STREAMING = ALLOW_STREAMING.lower() not in ['false', '0']

# Token validation
from datetime import datetime, timedelta

UTC_EPOCH       = datetime(1970, 1, 1)
MAX_TIME_DELTA  = timedelta(days=1)

#-----------------------------------------------------------------------------

class ResponseGenerator:
    """ Convenience wrapper around Flask response."""

    def __init__(self, mimetype):
        self._mimetype = mimetype
        self._outputs = []

        if mimetype not in ['application/json', 'text/plain']:
            raise ValueError('Invalid mimetype %r' % mimetype)

        self._headers = {
            'Content-Type': ('%s; charset=utf-8' % mimetype)
        }

    def add_header(self, header, value):
        self._headers[header] = value

    def add_output(self, output):
        """ Add either a string or string generator."""
        assert isinstance(output, (basestring, GeneratorType))
        self._outputs.append(output)

    def _get_generator(self):
        """ Glue generators into a single one that makes strings."""
        gen = flat_string_generator(self._outputs)

        if ALLOW_STREAMING:
            return gen

        log.warn('Streaming not allowed, serializing in memory.')

        rawstr = StringIO.StringIO()

        for string in gen:
            if isinstance(string, unicode):
                string = string.encode('utf-8')
            rawstr.write(string)

        return rawstr.getvalue()

    def generate(self):
        return Response(
            self._get_generator(),
            mimetype=self._mimetype,
            headers=self._headers)

def _token_error(token, message):
    errmsg = "Token '{}' is invalid: {}".format(token, message)
    raise ValueError(errmsg)

def _validate_token(request):

    token = request.args.get('token', 'null')

    try:
        if not token.startswith(READ_API_TOKEN):
            _token_error(token, 'not %s' % READ_API_TOKEN)

        utctime = token.replace(READ_API_TOKEN, '', 1)

        try:
            utctime = long(utctime)
        except ValueError as err:
            _token_error(token, "cannot parse '{}' ({})".format(
                utctime, err.message))

        ts_req  = UTC_EPOCH + timedelta(milliseconds=utctime)
        ts_diff = datetime.utcnow() - ts_req

        if abs(ts_diff) > MAX_TIME_DELTA:
            _token_error(token, 'time diff is {}'.format(ts_diff))

    except ValueError as err:
        log.exception('Invalid token, sending 403')
        abort(403) # forbidden


def _get_req_url(request):

    url = request.args.get('url')

    if not url:
        logging.error('URL parameter is not found in request')
        abort(400) # bad request

    if not url.startswith('http'):
        url = 'http://' + url;

    return url

def _create_document(url):

    # Configure urllib2
    httph = urllib2.HTTPHandler(debuglevel=APP_DEBUG)
    httpsh = urllib2.HTTPSHandler(debuglevel=APP_DEBUG)

    opener = urllib2.build_opener(httph, httpsh)
    urllib2.install_opener(opener)

    # Read raw html
    try:
        urlreq = urllib2.urlopen(url)
    except urllib2.URLError as err:
        log.error('urllib2 URL[%s] error: %s', url, err)
        abort(400) # bad request
    except urllib2.HTTPError as err:
        log.error('urllib2 HTTP error: %s', err)
        abort(error.code)

    meta = urlreq.info()

    log.info('Opening mime type "%s"', meta.gettype())

    rawhtml = urlreq.read()
    # Parse with readability
    doc = readability.Document(rawhtml)

    # Get readable html
    title, html = doc.short_title(), doc.summary()

    # Reformat as plain text
    txt = lhtml.tostring(lhtml.fromstring(html),
        method='text', encoding='utf-8')

    txt = txt.strip()
    txt = re.sub(r'\s+', r' ', txt, flags=re.MULTILINE)
    txt = re.sub(r'\)\.', r'). ', txt, flags=re.MULTILINE)

    # Create JSON object
    return {
        'url'       : url,
        'title'     : doc.short_title(),
        'author'    : None,
        'word_count': -1,
        'content'   : '<div>{}</div>'.format(txt),
    }


def _get_json(request):

    _validate_token(request)

    doc = _create_document(_get_req_url(request))

    response = ResponseGenerator('application/json')

    jsonp = request.args.get('callback')

    if jsonp:
        log.info('JSONP is enabled');
        # FIXME: Be more specific in CORS; for now rely on 'token'
        response.add_header('Access-Control-Allow-Origin', '*')

    if jsonp:
        response.add_output("%s(" % jsonp)

    response.add_output(json_generator(doc))

    if jsonp:
        response.add_output(")")

    return response.generate()


def _get_text(request):

    _validate_token(request)

    doc = _create_document(_get_req_url(request))

    response = ResponseGenerator('text/plain')

    for field in ['title', 'url', 'content']:
        value = doc[field]

        log.debug('Writing field %s of %r', field, type(value))

        response.add_output(value)
        response.add_output('\n\n')

    return response.generate()

def _log_env():
    log.info('Current version: %s', CURRENT_VERSION_ID)

#-----------------------------------------------------------------------------

from flask import request as flask_request
from flask import render_template

app = Flask(__name__,
        static_url_path='/assets')

_log_env()

@app.route('/api')
def root():
    return render_template('api.html')

@app.route('/json')
def json():
    return _get_json(flask_request)

@app.route('/text')
def text():
    return _get_text(flask_request)

def run(port, debug):
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    run(8080, True)

