import re
import unicodedata
from importlib import import_module

from django.apps import apps
from django.conf import settings

from rest_framework.routers import DefaultRouter

from .viewsets import get_viewsets
from .users import UserViewSet

class Restify(object):

    def __init__(self):
        # get restify specific settings
        self.settings  = getattr(settings, 'RESTIFY', {})
        
        self.IGNORE_LIST = ['^django*', '^api$', '^rest_framework*',
                            '^auth*'] + self.settings.get('IGNORE_LIST', [])
        self.router = None
        self.viewsets = {}   # viewsets
        self.apps()

    def slugify(self, value):
        try:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        except:
            pass
        value = re.sub('[^\w\s-]', '', value).strip().lower()

        return re.sub('[-\s]+', '-', value)

    def apps(self):
        all_apps = apps.app_configs
        
        for app, app_config in all_apps.iteritems():
            # Check if user is in ignored list
            found = [ignore_pattern for ignore_pattern in self.IGNORE_LIST if re.findall(ignore_pattern, app_config.name)]
            if found:
                continue

            for model in app_config.get_models():
                url = self.slugify(model._meta.verbose_name_plural.title())
                viewset = get_viewsets(model)

                self.viewsets[url] = viewset
            
    def register(self):
        self.router = DefaultRouter()
        for url, viewset in self.viewsets.iteritems():
            self.router.register(url, viewset)

        # special case fo User model
        self.router.register('users', UserViewSet)

        return self.router

    def router(self):
        return self.router

restify = Restify()
router = restify.register()
