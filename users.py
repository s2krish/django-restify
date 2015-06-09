from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import detail_route, list_route

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError

# for reset password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives


def send_mail(subject_template_name, email_template_name,
              context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        print body

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(id=self.request.user.id)

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
            message = {'uknown': _('Unknow error occured')}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        user_searlized = UserSerializers([user], many=True)
        return Response(user_searlized.data[0], status=status.HTTP_201_CREATED)

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
