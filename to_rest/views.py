from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models.fields.related import OneToOneField, ForeignKey, ManyToManyField
from django.db.models.fields.reverse_related import OneToOneRel, ManyToOneRel, ManyToManyRel
from django.http import HttpResponseBadRequest
from to_rest import constants
from to_rest import cfg

def oneToManyActionFactory(parentModel,childSerializer, field, relatedName):
    """for our purpose only"""
    childModel = field.model
    parentModelName = parentModel.__name__

    #@action(detail=True, methods=['get'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")
    def funcRelatedList(self,request,pk=None):
        parentObject = parentModel.objects.get(pk=pk)
        childObjects = eval("parentObject.{}.all()".format(relatedName))
        if len(childObjects) == 0:
            headers = {}
            headers[constants.CONTENT_MESSAGE] = constants.NO_OBJECT_EXISTS.format("related "+childModel.__name__)
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        else:
            page = self.paginate_queryset(childObjects)
            if page is not None:
                serializer =  childSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = childSerializer(childObjects, many=True)
            return Response(serializer.data)
    
    funcRelatedList.__name__ = "oneToManyList_" + relatedName
    funcRelatedList = action(detail=True, methods=['get'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")(funcRelatedList)

    #@action(detail=True, methods=['get'], url_path=relatedName + "/<childPk>", url_name=parentModelName.lower() + "-" + relatedName +"-retreive")
    def funcRelatedRetreive(self,request,childPk,pk=None):
        parentObject = parentModel.objects.get(pk=pk)
        childObject = eval("parentObject.{}.get(pk=childPk)".format(relatedName))
        serializer = childSerializer(childObject)
        return Response(serializer.data)
    
    funcRelatedRetreive.__name__ = "oneToManyRetreive_" + relatedName
    funcRelatedRetreive = action(detail=True, methods=['get'], url_path=relatedName + "/(?P<childPk>.+)", url_name=parentModelName.lower() + "-" + relatedName +"-retreive")(funcRelatedRetreive)
    return (funcRelatedList, funcRelatedRetreive)

def manyToManyActionFactory(parentModel, field, relatedName):
    """for our purpose only"""
    throughModel = eval("parentModel.{}.through".format(relatedName))
    throughModelName = throughModel.__name__
    parentModelName = parentModel.__name__
    metaAttributes = dict()
    metaAttributes["model"] = throughModel
    metaAttributes["fields"] = "__all__"
    meta = type("Meta", (object,), metaAttributes)
    serializerAttribute = {"Meta": meta}
    throughSerializer = type(throughModelName+"Serializer", (serializers.ModelSerializer,), serializerAttribute)
    
    #@action(detail=True, methods=['get'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")
    def funcRelatedList(self,request,pk=None):
        parentObject = parentModel.objects.get(pk=pk)
        throughObjects = eval("parentObject.{}.through.objects.all()".format(relatedName))
        if len(throughObjects) == 0:
            headers = {}
            headers[constants.CONTENT_MESSAGE] = constants.NO_OBJECT_EXISTS.format("related "+throughModel.__name__)
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        else:
            page = self.paginate_queryset(throughObjects)
            if page is not None:
                serializer =  throughSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = throughSerializer(throughObjects, many=True)
            return Response(serializer.data)
    
    funcRelatedList.__name__ = "manyToManyList_" + relatedName
    funcRelatedList = action(detail=True, methods=['get'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")(funcRelatedList)

    #@action(detail=True, methods=['get'], url_path=relatedName + "/(?P<childPk>.+)", url_name=parentModelName.lower() + "-" + relatedName +"-retreive")
    def funcRelatedRetreive(self,request,childPk,pk=None):
        parentObject = parentModel.objects.get(pk=pk)
        filter_param = field.field.m2m_field_name() + "_" + field.field.m2m_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_reverse_field_name() + "_" + field.m2m_reverse_target_field_name()
        throughObject = eval("parentObject.{}.through.objects.get({}=childPk)".format(relatedName,filter_param))
        serializer = throughSerializer(throughObject)
        return Response(serializer.data)
    
    funcRelatedRetreive.__name__ = "oneToManyRetreive_" + relatedName
    funcRelatedRetreive = action(detail=True, methods=['get'], url_path=relatedName + "/(?P<childPk>.+)", url_name=parentModelName.lower() + "-" + relatedName +"-retreive")(funcRelatedRetreive)
    return (funcRelatedList, funcRelatedRetreive)
    
def getObjectViewSetAttributes(model, modelSerializer, customViewParams):
    viewClassName = model.__name__ + "ViewSet"
    def list(self, request, *args, **kwargs):
        objects = self.get_queryset()
        if len(objects) == 0:
            headers = {}
            headers[constants.CONTENT_MESSAGE] = constants.NO_OBJECT_EXISTS.format(model.__name__)
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        else:
            page = self.paginate_queryset(objects)
            if page is not None:
                serializer =  self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(objects, many=True)
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
    if customViewParams is not None and customViewParams[constants.RETREIVE_METHOD] is not None:
        attributes["retrieve"] = customViewParams[constants.RETREIVE_METHOD]
    if customViewParams is not None and customViewParams[constants.UPDATE_METHOD] is not None:
        attributes["update"] = customViewParams[constants.UPDATE_METHOD]
    if customViewParams is not None and customViewParams[constants.DESTROY_METHOD] is not None:
        attributes["destroy"] = customViewParams[constants.DESTROY_METHOD]
    return attributes