from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from . import constants

def createObjectListView(model, modelSerializer, customViews):
    #getList
    def get(self, request, format=None):
        objects = model.objects.all()
        serializer = modelSerializer(objects, many=True)
        if len(objects) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.data)
    #create
    def post(self, request, format=None):
        serializer = modelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    attributes = {}
    if customViews is not None and customViews[constants.GET_OBJECT_LIST] is not None:
        attributes["get"] = customViews[constants.GET_OBJECT_LIST]
    else:
        attributes["get"] = get
    if customViews is not None and customViews[constants.CREATE_OBJECT] is not None:
        attributes["post"] = customViews[constants.CREATE_OBJECT]
    else:
        attributes["post"] = post
    viewCls = type(model.__name__ + "_ObjectListView", (APIView,), attributes)
    return viewCls

def createObjectDetailView(model, modelSerializer, customViews):
    #get the object
    def get_object(self,pk):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        modelObject = self.get_object(pk)
        serializer = modelSerializer(modelObject)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        modelObject = self.get_object(pk)
        serializer = modelSerializer(modelObject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        modelObject = self.get_object(pk)
        modelObject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    attributes = {}
    if customViews is not None and customViews[constants.GET_OBJECT] is not None:
        attributes["get"] = customViews[constants.GET_OBJECT]
    else:
        attributes["get_object"] = get_object
        attributes["get"] = get
    if customViews is not None and customViews[constants.UPDATE_OBJECT] is not None:
        attributes["put"] = customViews[constants.UPDATE_OBJECT]
    else:
        attributes["put"] = put
    if customViews is not None and customViews[constants.DELETE_OBJECT] is not None:
        attributes["delete"] = customViews[constants.DELETE_OBJECT]
    else:
        attributes["delete"] = delete

    viewCls = type(model.__name__ + "_ObjectDetailView", (APIView,), attributes)
    return viewCls