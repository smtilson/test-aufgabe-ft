from .views import (
    StoreViewSet,
    StoreManagersView,
    StoreDaysView,
    OwnerView,
    StoreHoursView,
)
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)),
    path("owner/", OwnerView.as_view()),
    path("stores/days/", StoreDaysView.as_view(), name="store-days"),
    path("stores/<int:pk>/days/", StoreDaysView.as_view(), name="store-days"),
    path("stores/hours/", StoreHoursView.as_view(), name="store-hours"),
    path("stores/hours/<int:pk>/", StoreHoursView.as_view(), name="store-hours"),
    path("stores/managers/", StoreManagersView.as_view(), name="store-managers"),
    path(
        "stores/managers/<int:pk>/", StoreManagersView.as_view(), name="store-managers"
    ),
]
