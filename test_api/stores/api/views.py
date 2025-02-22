from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    RetrieveModelMixin as Retrieve,
    ListModelMixin as List,
    UpdateModelMixin as Update,
    DestroyModelMixin as Destroy,
    CreateModelMixin as Create,
)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ..models import Store

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


# protect this with superuser permissions
class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
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


# this should be protected by manager and owner permissions


class StoreDaysView(
    List, Retrieve, Update, GenericAPIView
):  # Reorder mixins before GenericAPIView
    # print("StoreDaysView class loaded")
    serializer_class = DaysSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
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
        return self.partial_update(request, *args, **kwargs)


# this should be protected by manager and owner permissions
class StoreHoursView(GenericAPIView, List, Retrieve, Update):
    serializer_class = HoursSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
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
        return self.partial_update(request, *args, **kwargs)


# protect this with owner permissions
class StoreManagersView(GenericAPIView, List, Retrieve, Update):
    serializer_class = ManagersSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    pagination_class = StoreViewsPagination
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        return get_user_stores(self.request.user)

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
        return self.partial_update(request, *args, **kwargs)


# protect this with manager permissions
class ManagerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        stores = user.managed_stores.all()
        stores = stores.union(user.owned_stores.all())
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


# protect this with owner permissions
class OwnerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    # authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        stores = user.owned_stores.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


# Another approach would be to use a mixin class.
def get_user_stores(user):
    # print("User:", user)
    queryset = Store.objects.filter(
        Q(manager_ids__in=[user]) | Q(owner_id=user)
    ).distinct()
    # print("Queryset count:", queryset.count())
    return queryset


class StoreDaysListView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # print("StoreDaysListView loaded")

    def __init__(self, *args, **kwargs):
        # print("StoreDaysListView initialized")
        super().__init__(*args, **kwargs)

    def get(self, request):
        # print("List view GET called")
        return Response({"message": "This is the list view"}, status=status.HTTP_200_OK)


class StoreDaysDetailView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # print("StoreDaysDetailView loaded")

    def __init__(self, *args, **kwargs):
        # print("StoreDaysDetailView initialized")
        super().__init__(*args, **kwargs)

    def get(self, request, pk):
        # print("Detail view GET called")
        return Response(
            {"message": "This is the detail view"}, status=status.HTTP_200_OK
        )
