from to_rest import constants
from test_basics import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from test_basics import filterset
from to_rest.utils import ViewParams
from test_basics import models
from rest_framework.response import Response
from rest_framework.decorators import action

class CustomSerializer(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer
        return temp

class CustomAuthAndPermission(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
        temp[constants.PERMISSION_CLASSES] = [IsAuthenticatedOrReadOnly]
        return temp

class CustomThrottling(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.THROTTLE_SCOPE] = "studentCustomThrottle"
        return temp

class CustomFiltering(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.FILTER_BACKENDS] = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        temp[constants.FILTERSET_FIELDS] = ['name', 'year', 'discipline']
        temp[constants.SEARCH_FIELDS] = ['name']
        temp[constants.ORDERING_FIELDS] = ['discipline', 'year']
        temp[constants.ORDERING] = ['year']
        return temp


class CustomFiltering1(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.FILTER_BACKENDS] = [DjangoFilterBackend]
        temp[constants.FILTERSET_FIELDS] = ['name']
        temp[constants.FILTERSET_CLASS] = filterset.StudentWithFilterSetClassVSFilterSetFieldFilter
        
        return temp

class CustomListMethod(ViewParams):

    def getParams():
        def list(self, request, *args, **kwargs):
            objects = models.StudentWithCustomMethod.objects.filter(year=2)
            serializer = self.get_serializer(objects, many=True)
            return Response(serializer.data)
        temp = dict()
        temp['list'] = list
        return temp

class CustomAction(ViewParams):

    def getParams():
        def customaction(self, request, pk=None):
            obj = models.StudentWithCustomAction.objects.get(pk=pk)
            return Response({'msg':"custom action working for " + obj.name})
        customaction = action(detail=True, methods=['get'], url_name='customaction')(customaction)
        temp = dict()
        temp['customaction'] = customaction
        return temp