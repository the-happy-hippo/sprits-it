# coding: utf8
# Main app driver

import sys
import logging

from os import environ as ENV

HEROKU      = int(ENV.get('HEROKU', '0')) # running on the server
SERVER_PORT = int(ENV['PORT']) # listening port (mandatory)
APP_DEBUG   = int(ENV.get('APP_DEBUG', '0'))

def _setup_logging():
    """ Redirect stdout to the system log."""

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.NOTSET)

if __name__ == '__main__':

    _setup_logging()

    print 'HEROKU: server {} port {} dbg {}'.format(
        HEROKU, SERVER_PORT, APP_DEBUG)

    if HEROKU:
        print 'Production server detected, running gunicorn ...'
        from os import system; system('gunicorn spritsit:app')
    else:
        print 'Development server detected, running Flask test server ...'
        import spritsit; spritsit.run(port=SERVER_PORT, debug=APP_DEBUG)
