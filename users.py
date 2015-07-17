import django_filters

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q

# for reset password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route, list_route

# for backend filter
from rest_framework.filters import DjangoFilterBackend

"""
def send_mail(subject_template_name, email_template_name,
              context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
"""

# Customize BackendFilter to allow all fields.
class AllDjangoFilterBackend(DjangoFilterBackend):
    """
    A filter backend that uses django-filter.
    """

    def get_filter_class(self, view, queryset=None):
        """
        Return the django-filters `FilterSet` used to filter the queryset.
        """
        filter_class = getattr(view, 'filter_class', None)
        filter_fields = getattr(view, 'filter_fields', None)

        if filter_class or filter_fields:
            return super(AllDjangoFilterBackend, self).get_filter_class(self, view, queryset)

        class AutoFilterSet(self.default_filter_set):
            class Meta:
                model = queryset.model
                fields = None

        return AutoFilterSet


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = None


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

    @list_route(methods=['post'])
    def check_username(self, request):
        username = request.data.get('username', None)

        users = User.objects.filter(username=username)

        if len(users):
            content = {
                'found': True,
                'error': _('User with username %s already exists') % username
            }
        else:
            content = {
                'found': False,
                'error': _('No user exists with username %s') % username
            }

        return Response(content, status=status.HTTP_200_OK)

    @list_route(methods=['post'])
    def check_email(self, request):
        email = request.data.get('email', None)

        users = User.objects.filter(email=email)

        if len(users):
            content = {
                'found': True,
                'error': _('User with email %s already exists') % email
            }
        else:
            content = {
                'found': False,
                'error': _('No user exists with email %s') % email
            }

        return Response(content, status=status.HTTP_200_OK)


    @list_route(methods=['post'])
    def register(self, request):
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if not email or not username or not password:
            validation_message = _('This is requried field')
            content = {
                'email': [validation_message],
                'username': [validation_message],
                'password': [validation_message]
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            is_active = getattr(settings, "RESTIFY_NEW_USER_ACTIVE", False)
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

        user_searlized = UserSerializers([user], many=True)
        return Response(user_searlized.data[0], status=status.HTTP_201_CREATED)



"""
    @list_route(methods=['post'])
    def password_reset(self, request):
        template_name = 'registration/password_reset_form.html',
        email_template_name = 'registration/password_reset_email.html',
        subject_template_name = 'registration/password_reset_subject.txt',

        email = request.data.get('email', '')

        user = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True).latest('id')

        # print_r()
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }

        from_email = None

        context_email = context
        context_email['user'] = user

        send_mail(subject_template_name, email_template_name,
                  context_email, from_email, user.email,
                  html_email_template_name=None)

        return Response(context, status=status.HTTP_201_CREATED)
"""
