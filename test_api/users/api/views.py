from ..models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token


class CustomUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


@api_view(["POST"])
def register(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = CustomUser.objects.filter(email=email).first()
    if user is not None and user.check_password(password):
        token = user.auth_token
        return Response({"token": token.key})
