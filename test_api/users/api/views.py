from ..models import CustomUser
from .serializers import CustomUserSerializer, SignUpSerializer, LoginSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class SignupView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        print("performm_create called")
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        user.token = token.key

    def to_representation(self, instance):
        """Override to include token in the response."""
        data = super().to_representation(instance)
        data["token"] = instance.token  # Add token to the serialized data
        return data

    """
    def create(self, request, *args, **kwargs):
        print("create called")
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "User created successfully",
            "user": response.data,
            "token": "token.key",
        }
        print("response", response.data)
        return response
    """

    def get(self, request):
        msg = (
            "Send a POST request with first name, last name, email, and a "
            "password. Email will function as the username. An auth token "
            "will be returned."
        )
        return Response({"message": msg})


class Login1View(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)
            if user:
                return Response({"token": user.auth_token})
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Allows DRF GUI to show the form."""
        return Response({"message": "Send a POST request with email and password."})


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
                # is there a meaningful difference between returning
                # the token and just the token key?
                return Response({"token": user.auth_token.key})
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({"message": "Send a POST request with email and password."})
