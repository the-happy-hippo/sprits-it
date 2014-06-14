# -*- coding: utf-8 -*-
import json
import logging

from os import environ, path

#------------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

def _read_env():
    """ Read environment variables from .env file and put the values in
    ``os.environ``. This won't overwrite existing ``os.environ`` values.
    """
    envfile = path.join(path.dirname(__file__), '.env')

    log.info('Reading %s ...', envfile)

    with open(envfile) as fenv:
        for line in fenv.readlines():

            keyval = [ x.strip() for x in line.split('=') ]

            if keyval and len(keyval) == 2:
                key, val = keyval

                val = environ.get(key) or val # Don't overwrite existing values

                log.info('ENV: %s = %s', key, val)

                environ[key] = val

_read_env()

#------------------------------------------------------------------------------

# Google App Engine disallows dynamically built responses because
# it wants to know the response content length upfront :(
ALLOW_STREAMING = environ['ALLOW_STREAMING']

# Readability API token (mandatory)
READABILITY_API_KEY = environ.get('READABILITY_API_KEY')

# Google Analytics tracking ID (optional)
GOOG_ANALYTICS_ID = environ.get('GOOG_ANALYTICS_ID')

#------------------------------------------------------------------------------

ERROR_UNDEFINED_READABILITY_KEY = '''
Readability API key is undefined. Please get your key at
https://www.readability.com/developers/api and set it either
as an environment variable (e.g., with ``export READABILITY_API_KEY=<Key>``)
or in ``app/.env`` file.
'''
WARN_UNDEFINED_GOOG_ANALYTICS_ID = '''
Google Tracking ID is undefined. If you want your site to be tracked by Google \
Analytics, please register and get a tracking ID at \
http://www.google.com/analytics. Then set it either as an environment variable \
(e.g., with ``export GOOG_ANALYTICS_ID=<ID>``) or in ``app/.env`` file.
'''

#------------------------------------------------------------------------------

class Settings(object):
    """Global app settings stored in a JSON file and in env vars.
    """

    def __init__(self, filename='settings.json'):

        self._settings = Settings._read_json_settings(filename)

        allow_streaming = ALLOW_STREAMING.lower() not in ['false', '0']

        current_version = self._settings['current_version']

        # Current app version is preset by App Engine
        GAE_CURRENT_VERSION_ID = environ.get('CURRENT_VERSION_ID')

        if GAE_CURRENT_VERSION_ID is not None:
            gae_version_norm = GAE_CURRENT_VERSION_ID.replace('-', '.')
            current_version_norm = current_version.replace('-', '.')
            if not gae_version_norm.startswith(current_version_norm):
                raise ValueError(
                    "App version {} doesn't match GAE version {}".format(
                        current_version, GAE_CURRENT_VERSION_ID))
            self._settings['current_version'] = GAE_CURRENT_VERSION_ID

        self._settings['allow_streaming'] = allow_streaming

        if not GOOG_ANALYTICS_ID:
            log.warn(WARN_UNDEFINED_GOOG_ANALYTICS_ID.strip())

        self._settings['goog_analytics_id'] = GOOG_ANALYTICS_ID

        if not READABILITY_API_KEY:
            raise ValueError(ERROR_UNDEFINED_READABILITY_KEY.strip())

        self._settings['parsers']['Readability']['token'] = READABILITY_API_KEY

        log.info('App settings: %r', self._settings)

    @property
    def app_version(self):
        return self._settings['current_version']

    def get(self, key, default=None):
        return self.get(key, default)

    def __getitem__(self, key):
        return self._settings[key]

    def __getattr__(self, name):
        return self._settings[name]

    @staticmethod
    def _read_json_settings(filename):

        fullpath = path.join(path.dirname(__file__), filename)

        with open(fullpath) as fileobj:
            settings = json.load(fileobj, 'utf-8')

        return settings

# Global settings object
settings = Settings()

