from ..models import CustomUser
from .serializers import CustomUserSerializer, SignUpSerializer, LoginSerializer
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate


class CustomUserViewSet(ModelViewSet):
    # remove when not debugging.
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name", "email"]


class SignupView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    # remove after tests are written
    def perform_create(self, serializer):
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    # maybe remove after tests are written
    def create(self, request, *args, **kwargs):
        """Override create method to include the token in the response."""
        # Perform the object creation (user + token)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Create user and get token
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
                # is there a meaningful difference between returning
                # the token and just the token key?
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


# should there be a view for a owner to create a employee?
