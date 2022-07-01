from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models.fields.reverse_related import ManyToManyRel
from to_rest import constants

def oneToManyActionFactory(parentModel,childSerializer, field, relatedName):
    childModel = field.model
    parentModelName = parentModel.__name__

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
    
    funcRelatedList.__name__ = constants.ONE_TO_MANY_LIST_ACTION + relatedName
    funcRelatedList = action(detail=True, methods=['get'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")(funcRelatedList)
    return (funcRelatedList,)

def manyToManyActionFactory(parentModel, field, relatedName):
    throughModel = eval("parentModel.{}.through".format(relatedName))
    throughModelName = throughModel.__name__
    parentModelName = parentModel.__name__
    metaAttributes = dict()
    metaAttributes["model"] = throughModel
    metaAttributes["fields"] = "__all__"
    meta = type("Meta", (object,), metaAttributes)
    serializerAttribute = {"Meta": meta}
    throughSerializer = type(throughModelName+"Serializer", (serializers.ModelSerializer,), serializerAttribute)
    
    def funcRelatedList(self,request,pk=None):
        if self.request.method == "GET":
            parentObject = parentModel.objects.get(pk=pk)
            filter_param = field.field.m2m_reverse_field_name() + "_" + field.field.m2m_reverse_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_field_name() + "_" + field.m2m_target_field_name()
            throughObjects = eval("parentObject.{}.through.objects.filter({}=pk)".format(relatedName, filter_param))
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
        elif self.request.method == "POST":
            parentObject = parentModel.objects.get(pk=pk)
            providedData = request.data
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            providedData[parentObjectField] = pk
            serializer = throughSerializer(data=providedData)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
    funcRelatedList.__name__ = constants.MANY_TO_MANY_LIST_ACTION + relatedName
    funcRelatedList = action(detail=True, methods=['get', 'post'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")(funcRelatedList)

    def funcRelatedDetail(self,request,childPk,pk=None):
        if self.request.method == "PUT":
            parentObject = parentModel.objects.get(pk=pk)
            filter_param = field.field.m2m_field_name() + "_" + field.field.m2m_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_reverse_field_name() + "_" + field.m2m_reverse_target_field_name()
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            throughObject = eval("parentObject.{}.through.objects.get(pk=childPk)".format(relatedName))
            providedData = request.data
            providedData[parentObjectField] = pk
            serializer = throughSerializer(throughObject, data=providedData, partial=False)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        elif self.request.method == "PATCH":
            parentObject = parentModel.objects.get(pk=pk)
            filter_param = field.field.m2m_field_name() + "_" + field.field.m2m_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_reverse_field_name() + "_" + field.m2m_reverse_target_field_name()
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            throughObject = eval("parentObject.{}.through.objects.get(pk=childPk)".format(relatedName))
            providedData = request.data
            providedData[parentObjectField] = pk
            serializer = throughSerializer(throughObject, data=providedData, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        elif self.request.method == "DELETE":
            parentObject = parentModel.objects.get(pk=pk)
            filter_param = field.field.m2m_field_name() + "_" + field.field.m2m_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_reverse_field_name() + "_" + field.m2m_reverse_target_field_name()
            throughObject = eval("parentObject.{}.through.objects.get(pk=childPk)".format(relatedName))
            self.perform_destroy(throughObject)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    funcRelatedDetail.__name__ = constants.MANY_TO_MANY_DETAIL_ACTION + relatedName
    funcRelatedDetail = action(detail=True, methods=['put','patch','delete'], url_path=relatedName + "/(?P<childPk>.+)", url_name=parentModelName.lower() + "-" + relatedName +"-detail")(funcRelatedDetail)
    
    return (funcRelatedList, funcRelatedDetail)
    
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
    if customViewParams is not None and customViewParams.get(constants.GET_OBJECT_METHOD, None) is not None:
        attributes["get_object"] = customViewParams[constants.GET_OBJECT_METHOD]
    if customViewParams is not None and customViewParams.get(constants.GET_QUERYSET_METHOD, None) is not None:
        attributes["get_queryset"] = customViewParams[constants.GET_QUERYSET_METHOD]
    if customViewParams is not None and customViewParams.get(constants.LIST_METHOD, None) is not None:
        attributes["list"] = customViewParams[constants.LIST_METHOD]
    else:
        attributes["list"] = list
    if customViewParams is not None and customViewParams.get(constants.CREATE_METHOD, None) is not None:
        attributes["create"] = customViewParams[constants.CREATE_METHOD]
    if customViewParams is not None and customViewParams.get(constants.RETREIVE_METHOD, None) is not None:
        attributes["retrieve"] = customViewParams[constants.RETREIVE_METHOD]
    if customViewParams is not None and customViewParams.get(constants.UPDATE_METHOD, None) is not None:
        attributes["update"] = customViewParams[constants.UPDATE_METHOD]
    if customViewParams is not None and customViewParams.get(constants.PARTIAL_UPDATE_METHOD, None) is not None:
        attributes["partial_update"] = customViewParams[constants.PARTIAL_UPDATE_METHOD]
    if customViewParams is not None and customViewParams.get(constants.DESTROY_METHOD, None) is not None:
        attributes["destroy"] = customViewParams[constants.DESTROY_METHOD]
    return attributes