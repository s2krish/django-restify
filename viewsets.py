from django.conf import settings

from rest_framework import serializers
from rest_framework import viewsets

from . import import_attr


class Views(object):
    def __init__(self):
        self.restify_settings = getattr(settings, 'RESTIFY', {})
        self.restify_settings_serializers = self.restify_settings.get('SERIALIZERS', None)        

    def create_serializer(self, model):
        """Creates and returns serializers class"""
        meta_class = type('Meta', (), {})
        meta_class.model = model
        serializers_class = type('Serializer', (serializers.ModelSerializer, ), {})
        serializers_class.Meta = meta_class

        return serializers_class


    def get_serializer(self, model):
        """Retunrs serializers class. Checks settings if custom serializers is defined.
        If defined return custom class, otherwise creates new one"""

        # Check if there's custom serializer class
        model_name = model._meta.model_name
        custom_serializer_class = self.restify_settings_serializers.get(model_name, None)

        if custom_serializer_class:
            serializers_class = import_attr(custom_serializer_class)
        else:
            serializers_class = self.create_serializer(model)

        return serializers_class

    def create_vieset(self, model, serializers_class):
        """Creates and returns viewsets"""
        viewset_class = type('Viewset', (viewsets.ModelViewSet, ), {})
        viewset_class.queryset = model.objects.all()
        viewset_class.serializer_class = serializers_class

        # apply filter on all fields
        viewset_class.filter_fields = model._meta.get_all_field_names()

        return viewset_class

    def get_viewsets(self, model):
        """Creates and returns viewsets with serializer"""
        serializers_class = self.get_serializer(model)
        viewsets_class = self.create_vieset(model, serializers_class)

        return viewsets_class
