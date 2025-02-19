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
from django.db.models import Q
from ..models import Store
from .serializers import (
    StoreSerializer,
    DaysSerializer,
    HoursSerializer,
    ManagersSerializer,
)


# protect this with superuser permissions
class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

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
class StoreDaysView(GenericAPIView, List, Retrieve, Update):
    serializer_class = DaysSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        return get_user_stores(self.request.user)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            response = self.retrieve(request, *args, **kwargs)
            msg = (
                "Modify the days of operation by selecting or unselecting a given day."
            )
            response.data["message"] = msg
            return response
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        msg = "Modify the days of operation by selecting or unselecting a given day."
        response.data["message"] = msg
        return response


# this should be protected by manager and owner permissions
class StoreHoursView(GenericAPIView, List, Retrieve, Update):
    serializer_class = HoursSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

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


# protect this with owner permissions
class StoreManagersView(GenericAPIView, List, Retrieve, Update):
    serializer_class = ManagersSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

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
    return Store.objects.filter(Q(manager_ids__in=[user]) | Q(owner_id=user)).distinct()
