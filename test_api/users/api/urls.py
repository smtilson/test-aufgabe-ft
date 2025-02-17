from django.urls import path, include
from .views import CustomUserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r"users", CustomUserViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("login/", obtain_auth_token, name="login"),
]
