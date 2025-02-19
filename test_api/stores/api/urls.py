from .views import StoreViewSet, ManagerView, OwnerViewSet, OwnerView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="stores")
router.register("owner-stores", OwnerViewSet, basename="owner-stores")

urlpatterns = [
    path("", include(router.urls)),
    path("manager/", ManagerView.as_view()),
    path("owner/", OwnerView.as_view()),
]
