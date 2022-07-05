import traceback
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers
from django.db.models.fields.reverse_related import ManyToManyRel
from django.db.models.fields.related import ForeignKey
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from to_rest import constants
from rest_framework.viewsets import ModelViewSet
from to_rest import cfg

def isDefaultSerializer(serializer):
    return serializer.__name__.startswith(constants.PROJECT_NAME_PREFIX)


def getTempViewSet(childModel, childSerializer, viewParams):
    REST_FRAMEWORK_SETTINGS = settings.REST_FRAMEWORK
    defaultFilterBackends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #set defaults
    attributes = dict()
    attributes[constants.SERIALIZER_CLASS] = childSerializer
    attributes[constants.FILTER_BACKENDS] = defaultFilterBackends if REST_FRAMEWORK_SETTINGS is None else REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, defaultFilterBackends)
    if isDefaultSerializer(childSerializer):
        attributes[constants.FILTERSET_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.SEARCH_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.ORDERING_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation or x.many_to_one)]
    if viewParams is not None:
        attributes.update(viewParams)
    if attributes.get(constants.FILTERSET_CLASS, False):
        if attributes.get(constants.FILTERSET_FIELDS, False):
            del attributes[constants.FILTERSET_FIELDS]

    return type(constants.PROJECT_NAME_PREFIX + "temp_" + childModel.__name__, (ModelViewSet,), attributes)


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
    REST_FRAMEWORK_SETTINGS = settings.REST_FRAMEWORK
    childModel = field.related_model
    parentModelName = parentModel.__name__
    childCustomViewParams = None
    if cfg.djangoToRestRegistry.get(childModel.__name__, False):
        if cfg.djangoToRestRegistry[childModel.__name__].get(constants.CUSTOM_VIEW_PARAMS, False):
            childCustomViewParams = cfg.djangoToRestRegistry[childModel.__name__][constants.CUSTOM_VIEW_PARAMS]    


    def funcRelatedList(self,request,pk=None):
        parentObject = parentModel.objects.get(pk=pk)
        childObjects = eval("parentObject.{}.all()".format(relatedName))
        tempView = getTempViewSet(childModel, childSerializer, childCustomViewParams)
        tempViewObj = tempView()
        try:
            for backend in list(getattr(tempViewObj, constants.FILTER_BACKENDS)):
                childObjects = backend().filter_queryset(self.request, childObjects, tempViewObj)
        except Exception as e:
            traceback.print_exc()
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
    metaAttributes["fields"] = [x.name for x in throughModel._meta.get_fields()]
    meta = type("Meta", (object,), metaAttributes)
    serializerAttribute = {"Meta": meta}
    throughSerializer = type(constants.PROJECT_NAME_PREFIX + throughModelName+"Serializer", (serializers.ModelSerializer,), serializerAttribute)

    if cfg.djangoToRestRegistry.get(throughModelName, False):
        if cfg.djangoToRestRegistry[throughModelName].get(constants.CUSTOM_SERIALIZER, cfg.djangoToRestRegistry[throughModelName].get(constants.DEFAULT_SERIALIZER, False)):       
            throughSerializer = cfg.djangoToRestRegistry[throughModelName].get(constants.CUSTOM_SERIALIZER, cfg.djangoToRestRegistry[throughModelName][constants.DEFAULT_SERIALIZER])
    
    viewParams = None

    if cfg.djangoToRestRegistry.get(throughModel.__name__, False):
        if cfg.djangoToRestRegistry[throughModel.__name__].get(constants.CUSTOM_VIEW_PARAMS, False):
            viewParams = cfg.djangoToRestRegistry[throughModel.__name__][constants.CUSTOM_VIEW_PARAMS]
    
    def funcRelatedList(self,request,pk=None):
        #Kind of list view
        if self.request.method == "GET":
            #The listing will be of the through objects as it present more information about the relation when there
            # are additional information.
            parentObject = parentModel.objects.get(pk=pk)
            filter_param = field.field.m2m_reverse_field_name() + "_" + field.field.m2m_reverse_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_field_name() + "_" + field.m2m_target_field_name()
            throughObjects = eval("parentObject.{}.through.objects.filter({}=pk)".format(relatedName, filter_param))
            tempView = getTempViewSet(throughModel, throughSerializer, viewParams)
            tempViewObj = tempView()
            try:
                for backend in list(getattr(tempViewObj, constants.FILTER_BACKENDS)):
                    throughObjects = backend().filter_queryset(self.request, throughObjects, tempViewObj)
            except Exception as e:
                traceback.print_exc()
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
        objects = self.filter_queryset(self.get_queryset())
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
    REST_FRAMEWORK_SETTINGS = settings.REST_FRAMEWORK
    #add defaults
    defaultFilterBackends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    attributes["queryset"] = model.objects.all()
    attributes["serializer_class"] = modelSerializer
    attributes["list"] = list
    attributes[constants.FILTER_BACKENDS] = defaultFilterBackends if REST_FRAMEWORK_SETTINGS is None else REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, defaultFilterBackends)
    if isDefaultSerializer(modelSerializer):
        attributes[constants.FILTERSET_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.SEARCH_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.ORDERING_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation or x.many_to_one)]
    
    if customViewParams is not None:
        attributes.update(customViewParams)
    if attributes.get(constants.FILTERSET_CLASS, False):
        if attributes.get(constants.FILTERSET_FIELDS, False):
            del attributes[constants.FILTERSET_FIELDS]
        
    
    
    
    # if customViewParams is not None and customViewParams.get(constants.FILTER_BACKENDS, None) is not None:
    #     attributes[constants.FILTER_BACKENDS] = customViewParams[constants.FILTER_BACKENDS]
    # elif REST_FRAMEWORK_SETTINGS is not None and REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, None) is not None:
    #     attributes[constants.FILTER_BACKENDS] = REST_FRAMEWORK_SETTINGS[constants.DEFAULT_FILTER_BACKENDS]
    # else:
    #     attributes[constants.FILTER_BACKENDS] = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # if customViewParams is not None and customViewParams.get(constants.FILTERSET_CLASS, None) is not None:
    #     attributes[constants.FILTERSET_CLASS] = customViewParams[constants.FILTERSET_CLASS]
    # elif customViewParams is not None and customViewParams.get(constants.FILTERSET_FIELDS, None) is not None:
    #     attributes[constants.FILTERSET_FIELDS] = customViewParams[constants.FILTERSET_FIELDS]
    # elif isDefaultSerializer(modelSerializer):
    #     attributes[constants.FILTERSET_FIELDS] = [x.name for x in model._meta.get_fields() if not x.is_relation]
    # if customViewParams is not None and customViewParams.get(constants.ORDERING_FIELDS, None) is not None:
    #     attributes[constants.ORDERING_FIELDS] = customViewParams[constants.ORDERING_FIELDS]
    # elif isDefaultSerializer(modelSerializer):
    #     attributes[constants.ORDERING_FIELDS] = [x.name for x in model._meta.get_fields() if not x.is_relation]
    # if customViewParams is not None and customViewParams.get(constants.SEARCH_FIELDS, None) is not None:
    #     attributes[constants.SEARCH_FIELDS] = customViewParams[constants.SEARCH_FIELDS]
    # elif isDefaultSerializer(modelSerializer):
    #     attributes[constants.SEARCH_FIELDS] = [x.name for x in model._meta.get_fields() if not x.is_relation]
    # if customViewParams is not None and customViewParams.get(constants.ORDERING, None) is not None:
    #     attributes[constants.ORDERING] = customViewParams[constants.ORDERING] #No else to keep it to default
    
    # if customViewParams is not None and customViewParams.get(constants.GET_OBJECT_METHOD, None) is not None:
    #     attributes["get_object"] = customViewParams[constants.GET_OBJECT_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.GET_QUERYSET_METHOD, None) is not None:
    #     attributes["get_queryset"] = customViewParams[constants.GET_QUERYSET_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.LIST_METHOD, None) is not None:
    #     attributes["list"] = customViewParams[constants.LIST_METHOD]
    # else:
    #     attributes["list"] = list
    # if customViewParams is not None and customViewParams.get(constants.CREATE_METHOD, None) is not None:
    #     attributes["create"] = customViewParams[constants.CREATE_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.RETREIVE_METHOD, None) is not None:
    #     attributes["retrieve"] = customViewParams[constants.RETREIVE_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.UPDATE_METHOD, None) is not None:
    #     attributes["update"] = customViewParams[constants.UPDATE_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.PARTIAL_UPDATE_METHOD, None) is not None:
    #     attributes["partial_update"] = customViewParams[constants.PARTIAL_UPDATE_METHOD]
    # if customViewParams is not None and customViewParams.get(constants.DESTROY_METHOD, None) is not None:
    #     attributes["destroy"] = customViewParams[constants.DESTROY_METHOD]
    return attributes