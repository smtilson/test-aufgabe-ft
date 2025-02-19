from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PackageViewSet

# Create the router and register the viewset
router = DefaultRouter()
router.register(r"orders", OrderViewSet)
router.register(r"packages", PackageViewSet)


urlpatterns = [
    path("api/", include(router.urls)),  # Add the router's URLs to your main URLConf
]
