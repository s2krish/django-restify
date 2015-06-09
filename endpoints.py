import re
import unicodedata

from importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.conf import settings
from django.db.models.base import ModelBase
# from django.utils.text import slugify

from .viewsets import get_viewsets

from rest_framework.routers import DefaultRouter

from .users import UserViewSet

# for auth
from .auth import obtain_auth_token
from django.conf.urls import include, url

def slugify(value):
    try:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    except:
        pass
    value = re.sub('[^\w\s-]', '', value).strip().lower()

    return re.sub('[-\s]+', '-', value)


def endpoints():
    router = DefaultRouter()

    IGNORE_LIST = ('^django*', '^api$', '^rest_framework*')  # default ignore list

    # API_IGNORE_LIST can be set in django settings
    IGNORE_LIST += getattr(settings, 'API_IGNORE_LIST', ())

    for entry in settings.INSTALLED_APPS:
        found = [name for name in IGNORE_LIST if re.findall(name, entry)]
        if found:
            continue

        app = import_module(entry)

        if module_has_submodule(app, 'models'):
            models_module_name = '%s.%s' % (entry, 'models')

            # print models_module_name

            models = import_module(models_module_name)
            # print "------------%s--------------" % entry
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
                url = slugify(mod2._meta.verbose_name_plural.title())
                # print url
                viewset = get_viewsets(mod2)

                if url == 'users':
                    viewset.serializer_class.Meta.exclude = ('password', )
                else:
                    router.register(url, viewset)

    router.register('users', UserViewSet)


    return router

    # return urlpatterns   # + [url(r'^api-token-auth/', views.obtain_auth_token)]
