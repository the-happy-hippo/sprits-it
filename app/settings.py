# -*- coding: utf-8 -*-
import json
import logging

from os import environ, path

#------------------------------------------------------------------------------

# Google App Engine disallows dynamically built responses because
# it wants to know the response content length upfront :(
ALLOW_STREAMING = environ.get('ALLOW_STREAMING', '1')

# Readability API token (mandatory)
READABILITY_API_KEY = environ['READABILITY_API_KEY']

# Google Analytics tracking ID (optional)
GOOG_ANALYTICS_ID = environ.get('GOOG_ANALYTICS_ID')

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
        self._settings['goog_analytics_id'] = GOOG_ANALYTICS_ID

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

