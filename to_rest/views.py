from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from . import constants

def createObjectListView(model, modelSerializer, customViewParams):
    def list(self, request, *args, **kwargs):
        objects = self.get_queryset()
        serializer = modelSerializer(objects, many=True)
        if len(objects) == 0:
            headers = {}
            headers[constants.CONTENT_MESSAGE] = constants.NO_OBJECT_EXISTS.format(model.__name__)
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        else:
            return Response(serializer.data)
    
    attributes = {}
    attributes["queryset"] = model.objects.all()
    attributes["serializer_class"] = modelSerializer
    if customViewParams is not None and customViewParams[constants.GET_OBJECT_METHOD] is not None:
        attributes["get_object"] = customViewParams[constants.GET_OBJECT_METHOD]
    if customViewParams is not None and customViewParams[constants.GET_QUERYSET_METHOD] is not None:
        attributes["get_queryset"] = customViewParams[constants.GET_QUERYSET_METHOD]
    if customViewParams is not None and customViewParams[constants.LIST_METHOD] is not None:
        attributes["list"] = customViewParams[constants.LIST_METHOD]
    else:
        attributes["list"] = list
    if customViewParams is not None and customViewParams[constants.CREATE_METHOD] is not None:
        attributes["create"] = customViewParams[constants.CREATE_METHOD]
    viewCls = type(model.__name__ + "ListView", (generics.ListCreateAPIView,), attributes)
    return viewCls

def createObjectDetailView(model, modelSerializer, customViewParams):  
    attributes = {}
    attributes["queryset"] = model.objects.all()
    attributes["serializer_class"] = modelSerializer
    if customViewParams is not None and customViewParams[constants.GET_OBJECT_METHOD] is not None:
        attributes["get_object"] = customViewParams[constants.GET_OBJECT_METHOD]
    if customViewParams is not None and customViewParams[constants.GET_QUERYSET_METHOD] is not None:
        attributes["get_queryset"] = customViewParams[constants.GET_QUERYSET_METHOD]
    if customViewParams is not None and customViewParams[constants.RETREIVE_METHOD] is not None:
        attributes["retrieve"] = customViewParams[constants.RETREIVE_METHOD]
    if customViewParams is not None and customViewParams[constants.UPDATE_METHOD] is not None:
        attributes["update"] = customViewParams[constants.UPDATE_METHOD]
    if customViewParams is not None and customViewParams[constants.DESTROY_METHOD] is not None:
        attributes["destroy"] = customViewParams[constants.DESTROY_METHOD]
    viewCls = type(model.__name__ + "DetailView", (generics.RetrieveUpdateDestroyAPIView,), attributes)
    return viewCls