from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models.fields.reverse_related import ManyToManyRel
from to_rest import constants

def oneToManyActionFactory(parentModel,childSerializer, field, relatedName):
    """
    Method to create actions for view set for one to many relationship. Creation and updation
    of relationship can be handled from the other side of the relationship. Hence, no methods 
    for put,patch,delete. Since, there are use cases where an element of an entity can be
    related to an element of another entity more than once with other additional info. Hence,
    having a retreive method makes no sense by default. However, if required, custom actions
    can be provided as seen in decorators.py.

    Parameters:

        parentModel (django.db.models.Model): The model in the one to many side.

        childSerializer (rest_framework.serializers.ModelSerializer): Serializer for model in
        the other side.

        field (django.db.models.fields.Field): The field involved in the relationship.

        relatedName (str): The related name for the field.

    Returns:

        tuple of methods (tuple)

    """
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
    """
    Method to create actions for view set for many to many relationship. Since, there are 
    use cases where an element of an entity can be related to an element of another entity 
    more than once with other additional info. Hence, having a retreive method makes no 
    sense by default. Also, for the same reason, for update, partial_update and delete
    the primary key of the through model will be used as the path parameter for the nested url.
    However, if required, custom actions can be provided as seen in decorators.py.

    Parameters:

        parentModel (django.db.models.Model): The model in the one to many side.

        field (django.db.models.fields.Field): The field involved in the relationship.

        relatedName (str): The related name for the field.
    
    Returns:

        tuple of methods (tuple)

    """

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
        #Kind of list view
        if self.request.method == "GET":
            #The listing will be of the through objects as it present more information about the relation when there
            # are additional information.
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
            #To create new relation ship, through objects would be used as it contains prmary key
            #of both sides of the relationship
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
        #kind of detail view
        if self.request.method == "PUT":
            #For, updating a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
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
            #For, updating a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
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
            #For, deleting a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
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
    """
    Method to create all the attributes for view set.

    Parameters:

        model (django.db.models.Model) : The model for which the Viewset needs to be created

        modelSerializer (rest_framework.serialzers.ModelSerializer) : Corresponding model serializer fo the model.

        customViewParams (dict) : Dictionary of custom view attributes.
    
    Returns:

        attributes (dict): dictionary of view attributes
    """
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