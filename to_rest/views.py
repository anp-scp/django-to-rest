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
from django.shortcuts import get_object_or_404

REST_FRAMEWORK_SETTINGS = None
try:
    REST_FRAMEWORK_SETTINGS = settings.REST_FRAMEWORK
except Exception:
    pass

def listMethodFactory(modelName):
    def list(self, request, *args, **kwargs):
        objects = self.filter_queryset(self.get_queryset())
        if len(objects) == 0:
            headers = {}
            headers[constants.CONTENT_MESSAGE] = constants.NO_OBJECT_EXISTS.format("related "+modelName)
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        else:
            page = self.paginate_queryset(objects)
            if page is not None:
                serializer =  self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(objects, many=True)
            return Response(serializer.data)
    return list

def isDefaultSerializer(serializer):
    """
    Function to check if a serializer is default or custom.

    Parameters:
        serializer (BaseSerializer): the serializer object

    Returns:
        boolean
    """
    return serializer.__name__.startswith(constants.PROJECT_NAME_PREFIX)


def getTempViewSet(queryset, childModel, childSerializer, viewParams, extras):
    """
    Function to create temporary views for filtering and permission purposes for actions as
    actions do not accept additional filterset_class or filterset_fields.

    Parameters:
        queryset: the quesryset for the view
        childModel (django.db.models.Model) : the model object
        childSerializer (rest_framework.serializers.BaseSerializer) : the serializer
        viewParams (dict) : a dictionary for the view attributes
    
    Returns:
        ViewSet
    """
    
    defaultFilterBackends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #set defaults
    attributes = dict()
    attributes[constants.QUERYSET] = queryset
    attributes[constants.SERIALIZER_CLASS] = childSerializer
    #attributes[constants.FILTER_BACKENDS] = defaultFilterBackends if REST_FRAMEWORK_SETTINGS is None else REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, defaultFilterBackends)
    if REST_FRAMEWORK_SETTINGS is None or REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, None) is None:
        attributes[constants.FILTER_BACKENDS] = defaultFilterBackends
    if isDefaultSerializer(childSerializer):
        attributes[constants.FILTERSET_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.SEARCH_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation)] #no relational field by default as there could be large number of relational lookups possible
        attributes[constants.ORDERING_FIELDS] = [x.name for x in childModel._meta.get_fields() if (not x.is_relation or x.many_to_one)]
    #update with custom params
    if viewParams is not None:
        attributes.update(viewParams)
    if attributes.get(constants.FILTERSET_CLASS, False):
        if attributes.get(constants.FILTERSET_FIELDS, False):
            del attributes[constants.FILTERSET_FIELDS]#remove filterset_filds if filterset_class exists
    
    if extras is not None and extras.get('create', False):
        if not attributes.get('create', False):
            attributes['create'] = extras['create']
    
    if extras is not None and extras.get('list', False):
        if not attributes.get('list', False):
            attributes['list'] = extras['list']
    
    if extras is not None and extras.get('update', False):
        if not attributes.get('update', False):
            attributes['update'] = extras['update']
    
    if extras is not None and extras.get('get_object', False):
        if not attributes.get('get_object', False):
            attributes['get_object'] = extras['get_object']

    return type(constants.PROJECT_NAME_PREFIX + "temp_" + childModel._meta.label.replace('.','_'), (ModelViewSet,), attributes)


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
    childModel = field.related_model
    parentModelName = parentModel.__name__
    childCustomViewParams = None
    if cfg.djangoToRestRegistry.get(childModel._meta.label, False):
        if cfg.djangoToRestRegistry[childModel._meta.label].get(constants.CUSTOM_VIEW_PARAMS, False):
            childCustomViewParams = cfg.djangoToRestRegistry[childModel._meta.label][constants.CUSTOM_VIEW_PARAMS]    


    def funcRelatedList(self,request,pk=None, *args, **kwargs):
        parentObject = get_object_or_404(parentModel, pk=pk)
        childObjects = eval("parentObject.{}.all()".format(relatedName))
        tempViewSet = getTempViewSet(childObjects, childModel, childSerializer, childCustomViewParams, {'list': listMethodFactory(childModel.__name__)})
        tempView = tempViewSet.as_view({'get': 'list'})
        return tempView(request._request,*args,**kwargs)

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

    if cfg.djangoToRestRegistry.get(throughModel._meta.label, False):
        if cfg.djangoToRestRegistry[throughModel._meta.label].get(constants.CUSTOM_SERIALIZER, cfg.djangoToRestRegistry[throughModel._meta.label].get(constants.DEFAULT_SERIALIZER, False)):       
            throughSerializer = cfg.djangoToRestRegistry[throughModel._meta.label].get(constants.CUSTOM_SERIALIZER, cfg.djangoToRestRegistry[throughModel._meta.label][constants.DEFAULT_SERIALIZER])
    
    viewParams = None

    if cfg.djangoToRestRegistry.get(throughModel.__name__, False):
        if cfg.djangoToRestRegistry[throughModel.__name__].get(constants.CUSTOM_VIEW_PARAMS, False):
            viewParams = cfg.djangoToRestRegistry[throughModel.__name__][constants.CUSTOM_VIEW_PARAMS]

    def funcRelatedList(self,request,pk=None, *args,**kwargs):
        #Kind of list view
        if self.request.method == "GET":
            #The listing will be of the through objects as it present more information about the relation when there
            # are additional information.
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            filter_param = field.field.m2m_reverse_field_name() + "_" + field.field.m2m_reverse_target_field_name() if isinstance(field,ManyToManyRel) else field.m2m_field_name() + "_" + field.m2m_target_field_name()
            throughObjects = eval("throughModel.objects.filter({}=pk)".format(filter_param))
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'list': listMethodFactory(throughModelName)})
            tempView = tempViewSet.as_view({'get': 'list'})
            return tempView(request._request,*args,**kwargs)
            
        elif self.request.method == "POST":
            #To create new relation ship, through objects would be used as it contains prmary key
            #of both sides of the relationship
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            providedData = request.data.copy()
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            providedData[parentObjectField] = pk
            request._full_data = providedData
            throughObjects = parentModel.objects.all()
            def create(self, request, *args, **kwargs):
                serializer = self.get_serializer(data=providedData)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'create': create})
            tempView = tempViewSet.as_view({'post': 'create'})
            return tempView(request._request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
    funcRelatedList.__name__ = constants.MANY_TO_MANY_LIST_ACTION + relatedName
    funcRelatedList = action(detail=True, methods=['get', 'post'], url_path=relatedName, url_name=parentModelName.lower() + "-" + relatedName +"-list")(funcRelatedList)

    def funcRelatedDetail(self,request,childPk,pk=None,*args,**kwargs):
        #kind of detail view
        if self.request.method == 'GET':
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            throughObject = get_object_or_404(throughModel, pk=childPk)
            def get_object(self):
                return throughObject
            throughObjects = throughModel.objects.all()
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'get_object': get_object})
            tempView = tempViewSet.as_view({'get': 'retrieve'})
            return tempView(request._request, *args, **kwargs)
        elif self.request.method == "PUT":
            #For, updating a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            throughObject = get_object_or_404(throughModel, pk=childPk)
            providedData = request.data.copy()
            providedData[parentObjectField] = pk
            def get_object(self):
                return throughObject
            def update(self, request, *args, **kwargs):
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=providedData, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)
            throughObjects = throughModel.objects.all()
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'update': update, 'get_object': get_object})
            tempView = tempViewSet.as_view({'put': 'update'})
            return tempView(request._request, *args, **kwargs)
        elif self.request.method == "PATCH":
            #For, updating a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            parentObjectField = field.field.m2m_reverse_field_name()  if isinstance(field,ManyToManyRel) else field.m2m_field_name()
            throughObject = get_object_or_404(throughModel, pk=childPk)
            providedData = request.data.copy()
            providedData[parentObjectField] = pk
            def get_object(self):
                return throughObject
            def update(self, request, *args, **kwargs):
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=providedData, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)
            throughObjects = throughModel.objects.all()
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'update': update, 'get_object': get_object})
            tempView = tempViewSet.as_view({'patch': 'partial_update'})
            return tempView(request._request, *args, **kwargs)
        elif self.request.method == "DELETE":
            #For, deleting a relationship, through object will be used. For, that reason, the primary
            #key of the through object will be used as path parameter in the nested url. To get the primary
            #key of the through object filter can be used in with the url of list view (GET)
            parentObject = get_object_or_404(parentModel, pk=pk) #just to raise 404
            throughObject = get_object_or_404(throughModel, pk=childPk)
            def get_object(self):
                return throughObject
            throughObjects = throughModel.objects.all()
            tempViewSet = getTempViewSet(throughObjects, throughModel, throughSerializer, viewParams, {'get_object': get_object})
            tempView = tempViewSet.as_view({'delete': 'destroy'})
            return tempView(request._request, *args, **kwargs)
            # self.perform_destroy(throughObject)
            # return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    funcRelatedDetail.__name__ = constants.MANY_TO_MANY_DETAIL_ACTION + relatedName
    funcRelatedDetail = action(detail=True, methods=['get','put','patch','delete'], url_path=relatedName + "/(?P<childPk>.+)", url_name=parentModelName.lower() + "-" + relatedName +"-detail")(funcRelatedDetail)
    
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
    #add defaults
    defaultFilterBackends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    attributes["queryset"] = model.objects.all()
    attributes["serializer_class"] = modelSerializer
    attributes["list"] = list
    #attributes[constants.FILTER_BACKENDS] = defaultFilterBackends if REST_FRAMEWORK_SETTINGS is None else REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, defaultFilterBackends)
    if REST_FRAMEWORK_SETTINGS is None or REST_FRAMEWORK_SETTINGS.get(constants.DEFAULT_FILTER_BACKENDS, None) is None:
        attributes[constants.FILTER_BACKENDS] = defaultFilterBackends
    if isDefaultSerializer(modelSerializer):
        attributes[constants.FILTERSET_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation or x.many_to_one)]
        attributes[constants.SEARCH_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation)] #no relational field by default as there could be large number of relational lookups possible
        attributes[constants.ORDERING_FIELDS] = [x.name for x in model._meta.get_fields() if (not x.is_relation or x.many_to_one)]
    #update with custom params
    if customViewParams is not None:
        attributes.update(customViewParams)
    if attributes.get(constants.FILTERSET_CLASS, False):
        if attributes.get(constants.FILTERSET_FIELDS, False):
            del attributes[constants.FILTERSET_FIELDS]#remove filterset_filds if filterset_class exists

    return attributes