from .views import StoreViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
