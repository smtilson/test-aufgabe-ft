from .views import StoreViewSet, ManagerView, OwnerView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("manager/", ManagerView.as_view()),
    path("owner/", OwnerView.as_view()),
]
