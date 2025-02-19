from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from ..models import Store
from .serializers import StoreSerializer, OwnerStoreSerializer


# protect this with superuser permissions
class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        open_days = request.data.get("open_days", None)
        if open_days:
            store.open_days.add(*open_days)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        open_days = request.data.get("open_days", None)
        if open_days:
            store.open_days.add(*open_days)

        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


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


class OwnerViewSet(ModelViewSet):
    serializer_class = OwnerStoreSerializer
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Store.objects.filter(owner=user)
