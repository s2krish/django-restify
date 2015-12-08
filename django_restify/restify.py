import re
import unicodedata
from importlib import import_module

from django.apps import apps
from django.conf import settings

from rest_framework.routers import DefaultRouter

from .views import Views


def get_user_viewset():
    restify_settings = getattr(settings, 'RESTIFY', {})
    user_viewset = restify_settings.get('USER_VIEWSET', None)

    if user_viewset:
        user_module = import_module(user_viewset)
    else:
        user_module = import_module('django_restify.users')

    return getattr(user_module, 'UserViewSet')


class Restify(object):

    def __init__(self):
        # get restify specific settings
        self.settings = getattr(settings, 'RESTIFY', {})

        self.IGNORE_LIST = ['^django*', '^api$', '^rest_framework*',
                            '^auth*'] + self.settings.get('IGNORE_LIST', [])
        self.router = None
        self.viewsets = {}   # viewsets
        self.apps()

    def slugify(self, value):
        try:
            value = unicodedata.normalize('NFKD', value).encode(
                'ascii', 'ignore').decode('ascii')
        except:
            pass
        value = re.sub('[^\w\s-]', '', value).strip().lower()

        return re.sub('[-\s]+', '-', value)

    def get_apps(self):
        return apps.app_configs

    def apps(self):
        all_apps = self.get_apps()
        MODELS = self.settings.get('MODELS', None)

        for app, app_config in all_apps.items():
            # Check if user is in ignored list
            found = [ignore_pattern for ignore_pattern in self.IGNORE_LIST
                     if re.findall(ignore_pattern, app_config.name)]
            if found:
                continue

            for model in app_config.get_models():
                if MODELS and model._meta.model_name not in MODELS:
                    continue

                url = self.slugify(model._meta.verbose_name_plural.title())
                view = Views()
                viewset = view.get_viewsets(model)

                self.viewsets[url] = viewset

    def register(self):
        self.router = DefaultRouter()
        for url, viewset in self.viewsets.items():
            self.router.register(url, viewset)

        # special case fo User model
        user_viewset = get_user_viewset()
        self.router.register('users', user_viewset)

        return self.router

    def router(self):
        return self.router

restify = Restify()
router = restify.register()
