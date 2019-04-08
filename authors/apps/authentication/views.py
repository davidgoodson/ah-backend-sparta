import os
import jwt
from rest_framework import status, generics
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .renderers import UserJSONRenderer
from .serializers import (
LoginSerializer, RegistrationSerializer, UserSerializer, FacebookAuthSerializer, GoogleAuthSerializer, TwitterAuthSerializer
)
from .models import User


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        url = f"http://{get_current_site(request).domain}/api/users/verify?token={user_data.get('token')}"
    
        email = EmailMessage(
            subject='Authors Haven:Email-verification',
            body='Click here to verify your account {}'.format(url),
            from_email='authors.haven16@gmail.com',
            to=[user_data['email']],
        )
        email.send(fail_silently=False)
        return Response(user_data, status=status.HTTP_201_CREATED)

class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialAuthApiView(ListCreateAPIView):
    permissions_class = (AllowAny, )

    def post(self, request):
        """
        Fetch token from request, serialize and validate it
        """
        user_token = request.data.get('user_token', {})
        serializer = self.serializer_class(data=user_token)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)

class FacebookAuthApiView(SocialAuthApiView):
    serializer_class = FacebookAuthSerializer
    
class GoogleAuthApiView(SocialAuthApiView):
    serializer_class = GoogleAuthSerializer
    
class TwitterAuthApiView(SocialAuthApiView):
    serializer_class = TwitterAuthSerializer
    
class VerifyUserAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        token = request.query_params.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            id = payload.get('id')
            user = User.objects.filter(id=id).first()
            user.is_verified=True
            user.save()
            return Response(
                {
                    'Message': 'Account successfully verified, your free to  now login'
                },
                status=status.HTTP_200_OK)

        except Exception as identifier:
            return Response({"Message":"Something went wrong"})

       

