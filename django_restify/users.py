
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers

    # apply filter on all fields
    filter_fields = [f for f in User._meta.get_all_field_names()
                     if 'password' != f]

    def create(self, request, *args, **kwargs):
        error = {
            'post': _('Post method is not supported.'
                      'Use either /users/register or /auth/register')
        }
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'])
    def register(self, request):
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        restify_settings = getattr(settings, "RESTIFY", {})
        is_active = restify_settings.get('NEW_USER_ACTIVE', False)

        if not email or not username or not password:
            validation_message = _('This is requried field')
            content = {
                'email': [validation_message],
                'username': [validation_message],
                'password': [validation_message]
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            restify_settings = getattr(settings, "RESTIFY", {})
            is_active = restify_settings.get('NEW_USER_ACTIVE', False)
            user = User.objects.create_user(
                username,
                email,
                password
            )
            user.first_name = request.data.get('first_name', '')
            user.last_name = request.data.get('last_name', '')
            user.is_active = is_active
            user.save()
        except IntegrityError as e:
            message = {'error': e.message}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            message = {'error': _('Unknow error occured')}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        user_searlized = UserSerializers(user)
        return Response(user_searlized.data, status=status.HTTP_201_CREATED)
