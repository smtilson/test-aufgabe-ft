from .views import (
    StoreViewSet,
    StoreManagersView,
    StoreDaysView,
    StoreHoursView,
)
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)),
    path("days-list/", StoreDaysView.as_view(), name="store-days-list"),
    path("days-detail/<int:pk>/", StoreDaysView.as_view(), name="store-days-detail"),
    path("hours-list/", StoreHoursView.as_view(), name="store-hours-list"),
    path("hours-detail/<int:pk>/", StoreHoursView.as_view(), name="store-hours-detail"),
    path("managers-list/", StoreManagersView.as_view(), name="store-managers-list"),
    path(
        "managers-detail/<int:pk>/",
        StoreManagersView.as_view(),
        name="store-managers-detail",
    ),
]
