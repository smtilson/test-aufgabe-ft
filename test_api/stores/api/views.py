from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from ..models import Store
from .serializers import StoreSerializer


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]


class ManagerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        stores = user.managed_stores.all()
        stores = stores.union(user.owned_stores.all())
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class OwnerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        stores = user.owned_stores.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
