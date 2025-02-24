"""
Provides API views for managing custom user accounts and authentication.

The `CustomUserViewSet` class provides a set of API endpoints for managing custom user accounts. It uses the `CustomUserSerializer` to serialize and deserialize user data, and the `UserFilter` to filter the queryset.

The `SignupView` class provides an API endpoint for creating new user accounts. It uses the `SignUpSerializer` to validate and create new user instances, and returns an authentication token in the response.

The `LoginView` class provides an API endpoint for authenticating users and obtaining an authentication token. It uses the `LoginSerializer` to validate the user's email and password, and returns the authentication token if the credentials are valid.
"""

from ..models import CustomUser
from .serializers import CustomUserSerializer, SignUpSerializer, LoginSerializer
from .filters import UserFilter
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from .permissions import IsSuperUser


class CustomUserViewSet(ModelViewSet):
    permission_classes = [IsSuperUser]
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = CustomUserSerializer
    filterset_class = UserFilter


class SignupView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def create(self, request, *args, **kwargs):
        """Override create method to include the token in the response."""
        # Create user and get token
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = self.perform_create(serializer)

        # Get user_data and add token
        user_data = serializer.data
        user_data["token"] = token
        return Response(user_data, status=status.HTTP_201_CREATED)

    def get(self, request):
        msg = (
            "Send a POST request with first name, last name, email, and a "
            "password. Email will function as the username. An auth token "
            "will be returned."
        )
        return Response({"message": msg})


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer  # DRF will now auto-generate the form

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)
            if user:
                return Response({"token": user.auth_token.key})
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Allows for API-GUI form."""
        msg = (
            "Send a POST request with email and password to login and receive a token."
        )
        return Response({"message": msg})
