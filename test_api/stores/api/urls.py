from .views import StoreViewSet, ManagerView, StoreDaysView, OwnerView, StoreHoursView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)),
    path("manager/", ManagerView.as_view()),
    path("owner/", OwnerView.as_view()),
    path("stores/<int:pk>/days/", StoreDaysView.as_view()),
    path("stores/<int:pk>/hours/", StoreHoursView.as_view()),
]
