# -*- coding: utf-8 -*-
import re
import urllib2
import StringIO
import logging

try:
    import local_settings
except ImportError: pass

from types import GeneratorType
from settings import settings
from extractor import extractor

from lazygen import flat_string_generator, compression_generator

import fixpath

from flask import abort, Response

#-----------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------

# Dumb authorization for now (mandatory)
READ_API_TOKEN = settings.parsers['SpritsIt']['token']

#-----------------------------------------------------------------------------

# Token validation
from datetime import datetime, timedelta

UTC_EPOCH       = datetime(1970, 1, 1)
MAX_TIME_DELTA  = timedelta(days=1)

#-----------------------------------------------------------------------------

class ResponseGenerator:
    """ Convenience wrapper around Flask response."""

    def __init__(self, mimetype, compression=None):
        self._mimetype = mimetype
        self._compression = compression
        self._outputs = []

        if mimetype not in ['application/json', 'text/plain']:
            raise ValueError('Invalid mimetype %r' % mimetype)

        self._headers = {
            'Content-Type': ('%s; charset=utf-8' % mimetype)
        }

        if compression:
            self.add_header('content-encoding', compression)

    def add_header(self, header, value):
        self._headers[header] = value

    def add_output(self, output):
        """ Add either a string or string generator."""
        assert isinstance(output, (basestring, GeneratorType))
        self._outputs.append(output)

    def _get_generator(self):
        """ Glue generators into a single one that makes strings."""
        gen = flat_string_generator(self._outputs)

        if self._compression:
            log.debug('Compression allowed, method: %s', self._compression)
            gen = compression_generator(gen, self._compression)

        if settings.allow_streaming:
            log.info('Streaming is allowed, serializing on the fly.')
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

    # Read raw html
    try:
        json_object = extractor.extract(url)
    except urllib2.URLError as err:
        log.error('urllib2 URL[%s] error: %s', url, err)
        abort(400) # bad request
    except urllib2.HTTPError as err:
        log.error('urllib2 HTTP error: %s', err)
        abort(error.code)

    return json_object

def _get_compression(accept_encodings):
    encodings = [enc.strip().lower()
        for enc in accept_encodings.split(',')]

    for enc in encodings:
        if enc in ['deflate', 'gzip']:
            return enc

    return None

def _get_json(request):

    _validate_token(request)

    doc = _create_document(_get_req_url(request))

    compression = _get_compression(
        request.headers.get('accept-encoding', ''))

    response = ResponseGenerator('application/json', compression)

    jsonp = request.args.get('callback')

    if jsonp:
        log.debug('JSONP is enabled');
        response.add_output("%s(" % jsonp)

    response.add_output(doc.json_generator())

    if jsonp:
        response.add_output(")")

    return response.generate()


def _get_text(request):

    _validate_token(request)

    doc = _create_document(_get_req_url(request))

    response = ResponseGenerator('text/plain')

    for field in ['title', 'url', 'content']:
        value = getattr(doc,field)

        log.debug('Writing field %s of %r', field, type(value))

        response.add_output(value)
        response.add_output('\n\n')

    return response.generate()

def _log_env():
    log.info('Current version: %s', settings.app_version)

def _urllib_config():
    # Configure urllib2
    debug_level = settings.app_debug

    httph = urllib2.HTTPHandler(debuglevel=debug_level)
    httpsh = urllib2.HTTPSHandler(debuglevel=debug_level)
    opener = urllib2.build_opener(httph, httpsh)

    urllib2.install_opener(opener)

def _startup():
    log.info('Starting %s' % __file__)

    _log_env()

    _urllib_config()

#-----------------------------------------------------------------------------

from flask import Flask
from flask import request as flask_request
from flask import render_template

app = Flask(__name__,
        static_url_path='/assets')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

@app.route('/sitemap')
def sitemap():
    return app.send_static_file('sitemap.txt')

@app.route('/unsupported')
def unsupported():
    return app.send_static_file('unsupported.html')

@app.route('/')
@app.route('/read')
def index():
    return render_template('index.html', version=settings.app_version)

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/json')
def json():
    return _get_json(flask_request)

@app.route('/text')
def text():
    return _get_text(flask_request)

def run(port, debug):
    app.run(host='0.0.0.0', port=port, debug=debug)

_startup()

if __name__ == '__main__':
    run(8080, True)

