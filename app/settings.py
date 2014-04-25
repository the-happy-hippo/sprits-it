# -*- coding: utf-8 -*-
import json
import logging

from os import environ, path

#------------------------------------------------------------------------------

# Google App Engine disallows dynamically built responses because
# it wants to know the response content length upfront :(
ALLOW_STREAMING = environ.get('ALLOW_STREAMING', '1')

# Current app version (mandatory)
CURRENT_VERSION_ID = environ['CURRENT_VERSION_ID']

#------------------------------------------------------------------------------

# App logger
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class Settings(object):
    """Global app settings stored in a JSON file and in env vars.
    """

    def __init__(self, filename='settings.json'):

        self._settings = Settings._read_json_settings(filename)

        allow_streaming = ALLOW_STREAMING.lower() not in ['false', '0']

        self._settings['current_version'] = CURRENT_VERSION_ID
        self._settings['allow_streaming'] = allow_streaming

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

