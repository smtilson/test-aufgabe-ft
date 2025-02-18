from django.urls import path, include
from .views import CustomUserViewSet, SignupView, LoginView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"users", CustomUserViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
]
