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
from ..models import Store
from .serializers import StoreSerializer, StoreDaysSerializer, StoreHoursSerializer


# protect this with superuser permissions
class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]


# this should be protected by manager and owner permissions
class StoreDaysView(GenericAPIView, List, Retrieve, Update):
    queryset = Store.objects.all()
    serializer_class = StoreDaysSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# this should be protected by manager and owner permissions
class StoreHoursView(GenericAPIView, List, Retrieve, Update):
    queryset = Store.objects.all()
    serializer_class = StoreHoursSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if pk:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
