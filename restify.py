import re
import unicodedata

from importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.conf import settings
from django.db.models.base import ModelBase

from .viewsets import get_viewsets

class Restify(object):

    def __init__(self):
        self.IGNORE_LIST = ('^django*', '^api$')  # default ignore list
        self.viewsets = {}   # viewsets
        self.module = ()   # keep track of imported Django App (installed App)
        self.model = ()   # keep track of imported model of an Django App

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
            self.module += (entry, )   # for preventing reimport

            if module_has_submodule(app, 'models'):
                models_module_name = '%s.%s' % (entry, 'models')

                # do not import model if it already imported
                if models_module_name in self.model:
                    continue

                models = import_module(models_module_name)

                self.model += (models_module_name, )  # for preventing reimport

                for mod in dir(models):
                    try:
                        mod2 = getattr(models, mod)
                    except:
                        continue

                    # print "mod ", mod2._meta.abstract

                    if not isinstance(mod2, ModelBase) or getattr(mod2._meta, 'abstract', None):
                        continue

                    # print mod

                    # actual model to register api
                    # print mod2._meta.verbose_name_plural.title()
                    url = self.slugify(mod2._meta.verbose_name_plural.title())
                    # print url
                    viewset = get_viewsets(mod2)

                    if url == 'users':
                        viewset.serializer_class.Meta.exclude = ('password', )

                    self.viewsets[url] = viewset

    def register(self):
        if url == 'users':
            viewset.serializer_class.Meta.exclude = ('password', )
        else:
            router.register(url, viewset)
        # print self.viewsets

restify = Restify()
