from django.conf import settings

from rest_framework import serializers
from rest_framework import viewsets

from . import import_attr


class Views(object):

    def __init__(self):
        self.restify_settings = getattr(settings, 'RESTIFY', {})
        self.restify_settings_serializers = self.restify_settings.get(
            'SERIALIZERS', {})
        self.restify_settings_viewsets = self.restify_settings.get(
            'VIEWSETS', {})

    def create_serializer(self, model):
        """Creates serializers class dynamically for given model"""
        meta_class = type('Meta', (), {})
        meta_class.model = model
        serializer_class = type(
            'Serializer', (serializers.ModelSerializer, ), {})
        serializer_class.Meta = meta_class

        return serializer_class

    def get_serializer(self, model):
        """Retunrs serializer class. Checks settings if custom serializer is defined.
        If defined return custom class, otherwise creates new one"""

        # Check if there's custom serializer class
        model_name = model._meta.model_name
        custom_serializer_class = self.restify_settings_serializers.get(
            model_name, None)

        if custom_serializer_class:
            serializer_class = import_attr(custom_serializer_class)
        else:
            serializer_class = self.create_serializer(model)

        return serializer_class

    def get_viewset(self, model):
        """Retunrs viewset class. Checks settings if custom vieset is defined.
        If defined return custom class, otherwise creates new one"""

        # Check if there's custom serializer class
        model_name = model._meta.model_name
        custom_viewset_class = self.restify_settings_viewsets.get(
            model_name, None)

        if custom_viewset_class:
            viewset_class = import_attr(custom_viewset_class)
        else:
            viewset_class = None

        return viewset_class

    def create_viewset(self, model, serializer_class):
        """Creates viewsets dynamically for model"""
        viewset_class = type('Viewset', (viewsets.ModelViewSet, ), {})
        viewset_class.queryset = model.objects.all()

        viewset_class.serializer_class = serializer_class
        viewset_class.filter_fields = model._meta.get_all_field_names()

        return viewset_class

    def get_viewsets(self, model):
        """Creates and returns viewsets with serializer"""
        viewsets_class = self.get_viewset(model)

        if not viewsets_class:
            serializer_class = self.get_serializer(model)
            viewsets_class = self.create_viewset(model, serializer_class)

        return viewsets_class
