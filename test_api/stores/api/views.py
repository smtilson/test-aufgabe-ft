"""
This module contains the API views for the stores application.

The `StoreViewSet` class is a ModelViewSet that provides CRUD operations for the `Store` model. It uses the `StoreSerializer` to serialize the data, and the `StoreFilter` to filter the queryset. The `StoreViewsPagination` class is used to paginate the results.

The `StoreDaysView` class is a GenericAPIView that provides GET, PUT, and PATCH operations for the days of operation of a store. It uses the `DaysSerializer` to serialize the data, and the `DaysFilter` to filter the queryset.

The `StoreHoursView` class is a GenericAPIView that provides GET, PUT, and PATCH operations for the hours of operation of a store. It uses the `HoursSerializer` to serialize the data, and the `HoursFilter` to filter the queryset.

The `StoreManagersView` class is a GenericAPIView that provides GET, PUT, and PATCH operations for the managers of a store. It uses the `ManagersSerializer` to serialize the data, and the `ManagersFilter` to filter the queryset.

The `get_user_stores` function is a helper function that returns the stores that the user has access to, based on their role (superuser or manager).

The `is_list_view` function is a helper function that checks if the current request is a list view.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    RetrieveModelMixin as Retrieve,
    ListModelMixin as List,
    UpdateModelMixin as Update,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ..models import Store
from .filters import StoreFilter, DaysFilter, HoursFilter, ManagersFilter
from .serializers import (
    StoreSerializer,
    DaysSerializer,
    HoursSerializer,
    ManagersSerializer,
)


class StoreViewsPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
    filterset_class = StoreFilter
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        return get_user_stores(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        msg = "Modify all aspects of a store by filling the relevant field."
        response.data["message"] = msg
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        msg = "Create a store by filling the relevant fields."
        response.data["message"] = msg
        return response


class StoreDaysView(List, Retrieve, Update, GenericAPIView):
    serializer_class = DaysSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
    filterset_class = DaysFilter
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        return get_user_stores(self.request.user)

    def get(self, request, *args, **kwargs):
        if kwargs.get("pk", None):
            response = self.retrieve(request, *args, **kwargs)
            msg = (
                "Modify the days of operation by selecting or unselecting a given day."
            )
            response.data["message"] = msg
            return response

        response = self.list(request, *args, **kwargs)
        msg = "Select store to modify its days of operation."
        response.data["message"] = msg
        return response

    def patch(self, request, *args, **kwargs):
        if is_list_view(request):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return self.partial_update(request, *args, **kwargs)


class StoreHoursView(GenericAPIView, List, Retrieve, Update):
    serializer_class = HoursSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
    filterset_class = HoursFilter
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        return get_user_stores(self.request.user)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            response = self.retrieve(request, *args, **kwargs)
            msg = "Modify the hours of operation using the given fields."
            response.data["message"] = msg
            return response
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        msg = "Modify the hours of operation using the given fields."
        response.data["message"] = msg
        return response

    def patch(self, request, *args, **kwargs):
        if is_list_view(request):
            return Response(status=status.HTTP_405_METHOD_NOT)
        return self.partial_update(request, *args, **kwargs)


class StoreManagersView(GenericAPIView, List, Retrieve, Update):
    serializer_class = ManagersSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
    filterset_class = ManagersFilter
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        return Store.objects.filter(Q(owner_id=self.request.user))

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            response = self.retrieve(request, *args, **kwargs)
            msg = "Modify the managers of the store by selecting a given user."
            msg += " Selecting a user that is already a manager will remove their manager status."
            response.data["message"] = msg
            return response
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        msg = "Modify the managers of the store by selecting a given user."
        msg += " Selecting a user that is already a manager will remove their manager status."
        response.data["message"] = msg
        return response

    def patch(self, request, *args, **kwargs):
        if is_list_view(request):
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return self.partial_update(request, *args, **kwargs)


# Another approach would be to use a mixin class.
def get_user_stores(user):
    if user.is_superuser:
        return Store.objects.all()
    return Store.objects.filter(Q(manager_ids__in=[user]) | Q(owner_id=user)).distinct()


def is_list_view(request):
    return "list" in request.path
