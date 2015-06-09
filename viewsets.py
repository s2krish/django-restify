from rest_framework import serializers
from rest_framework import viewsets


def create_serializer(model):
    meta_class = type('Meta', (), {})
    meta_class.model = model
    serializer_class = type('Serializer', (serializers.ModelSerializer, ), {})
    serializer_class.Meta = meta_class

    return serializer_class


def create_vieset(model, serializers_class):
    viewset_class = type('Viewset', (viewsets.ModelViewSet, ), {})
    viewset_class.queryset = model.objects.all()
    viewset_class.serializer_class = serializers_class

    return viewset_class


def get_viewsets(entry):
    serializers_class = create_serializer(entry)
    viewsets_class = create_vieset(entry, serializers_class)

    return viewsets_class
