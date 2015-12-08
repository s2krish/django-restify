django-restify
==============

:code:`django-restify` requires :code:`django-rest-framework`. It will create RESTFul endpoints for all models that are enabled in your project. 

Installation
============

.. code:: bash

   pip install django_restify


Uses
====

1. Install django-rest-framework and django_restify.
2. Activate :code:`django-rest-framework` and :code:`django_restify` by adding it in :code:`INSTALLED_APP` of your django settings

   .. code:: Python
	     
      INSTALLED_APP = (
	     'django.contrib.auth',
	      (...),
	      'rest_framework',
	      'django_restify'
      )
3. Configure :code:`urls.py`:

   Import :code:`django_restify.router:`

   .. code:: Python

      from django_restify.restify import router

   Configure URL:
   
   .. code:: Python

      urlpatterns = [
	     url(r'^admin/', include(admin.site.urls)),
	     (.......),
	     url(r'^api/v1/', include(router.urls)),
      ]

Settings
========

.. code:: Python

   RESTIFY = {
      'MODELS': [],
      'IGNORE_LIST': [],
      'USER_VIEWSET': '',
      'NEW_USER_ACTIVE': True,
      'SERIALIZERS': {
          'model': {},
      },
      'VIEWSETS': {
          'entry': {},
      }
  }


MODELS
------

The list of models that you want create REST end-point. It will ingnore all other models and create end points models as listed in :code:`MODELS`. :code:`IGNORE_LIST` will get higher precedence over :code:`MODELS`.

IGNORE_LIST
-----------

The modules to be ignored (in list format). It can accept regular expression. For example, the default ignore list looks like:

.. code:: Python

    ['^django*', '^api$', '^rest_framework*', '^auth*'] 

USER_VIEWSET
------------

To use custom viewset for user model

NEW_USER_ACTIVE
---------------

Set new registered user as active.

SERIALIZERS
-----------

To use custom serializers for a model. It should be in dictionary format e.g. :code:`{'model': 'package.serializers.ModelSerializer'}`

VIEWSETS
--------

To use custom viewsets for a model. It should be dictionary format e.g. :code:`{'model': 'package.viewsets.ModelViewSet'}`
