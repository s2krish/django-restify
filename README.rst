Turn your Django project into RESTFul APIs in one minute.

django-restify requires django-rest-framework. It will create RESTFul endpoints for all models that enabled in your project. 

Uses
####

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
