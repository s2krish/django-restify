import re
import unicodedata

from rest_framework.routers import DefaultRouter

from importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.conf import settings
from django.db.models.base import ModelBase

from .viewsets import get_viewsets
from .users import UserViewSet

class Restify(object):

    def __init__(self):
        self.IGNORE_LIST = ('^django*', '^api$', '^rest_framework*',
                            '^auth*')  # default ignore list
        self.router = None
        self.viewsets = {}   # viewsets
        self.module = ()   # keep track of imported Django App (installed App)
        self.model = ()   # keep track of imported model of an Django App

        self.apps()

    def slugify(self, value):
        try:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        except:
            pass
        value = re.sub('[^\w\s-]', '', value).strip().lower()

        return re.sub('[-\s]+', '-', value)

    def apps(self):
        self.IGNORE_LIST += getattr(settings, 'RESTIFY_IGNORE_LIST', ())

        for entry in settings.INSTALLED_APPS:
            found = [name for name in self.IGNORE_LIST if re.findall(name, entry)]
            if found or entry in self.module:
                continue

            app = import_module(entry)
            self.module += (entry, )

            # print entry

            if module_has_submodule(app, 'models'):
                models_module_name = '%s.%s' % (entry, 'models')

                models = import_module(models_module_name)

                for mod in dir(models):

                    # do not import model if it already imported
                    if mod in self.model:
                        continue

                    # skip auth User model
                    if mod.lower() == 'user':
                        continue

                    self.model += (mod, )

                    try:
                        mod2 = getattr(models, mod)
                    except:
                        continue

                    if not isinstance(mod2, ModelBase) or getattr(mod2._meta, 'abstract', None):
                        continue

                    url = self.slugify(mod2._meta.verbose_name_plural.title())
                    # print url
                    viewset = get_viewsets(mod2)

                    self.viewsets[url] = viewset

        print self.model

    def register(self):

        # print self.viewsets

        self.router = DefaultRouter()
        for url, viewset in self.viewsets.iteritems():
            self.router.register(url, viewset)

        # special case for auth User model
        self.router.register('users', UserViewSet)

        return self.router

    def router(self):
        return self.router

restify = Restify()
router = restify.register()
