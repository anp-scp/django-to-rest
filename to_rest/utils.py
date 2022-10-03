from to_rest import cfg
from django.apps import apps
from to_rest import constants
from to_rest import serializers as restifySerializer
from to_rest import views
from django.urls import path
from rest_framework.viewsets import ModelViewSet
from rest_framework import routers
from abc import ABC, abstractmethod
import importlib

class ViewParams(ABC):
    """
    Abstract class to provide custom view parameters. This class needs to be inherited to provide
    custom view params.
    """

    @abstractmethod
    def getParams():
        pass

def restifyApp(relativeUri):
    """
    The function to restify an app. This will iterate over the models of the appName and will
    create ModelSerializers for the models, will create viewsets and will hook them with
    routes

    Prameters:
        relativeUri: (string): The relative url for the api
    Return:
        list of urls (list)
    """

    for entity in cfg.djangoToRestRegistry:
        if cfg.djangoToRestRegistry[entity].get(constants.CUSTOM_VIEW_PARAMS,False) and isinstance(cfg.djangoToRestRegistry[entity].get(constants.CUSTOM_VIEW_PARAMS,False), str):
            temp = cfg.djangoToRestRegistry[entity][constants.CUSTOM_VIEW_PARAMS]
            appName = apps.get_model(entity)._meta.app_label
            module = importlib.import_module(appName + '.' + 'view_params')
            temp = getattr(module, temp)
            customViewParams = temp.getParams()
            cfg.djangoToRestRegistry[entity][constants.CUSTOM_SERIALIZER] = customViewParams.pop(constants.SERIALIZER_CLASS, None)
            cfg.djangoToRestRegistry[entity][constants.CUSTOM_VIEW_PARAMS] = customViewParams
    
    for entity in cfg.djangoToRestRegistry:
        model = apps.get_model(entity)
        customSerializer = cfg.djangoToRestRegistry[entity].get(constants.CUSTOM_SERIALIZER,None)
        customViewParams = cfg.djangoToRestRegistry[entity].get(constants.CUSTOM_VIEW_PARAMS,None)
        excludedFields = cfg.djangoToRestRegistry[entity].get(constants.EXCLUDE_FIELDS, None)
        methodFields = cfg.djangoToRestRegistry[entity].get(constants.METHOD_FIELDS, None)
        modelSerializer = None
        if customSerializer is None:
            modelSerializer = restifySerializer.createModelSerializers(model, excludedFields, methodFields)
            cfg.djangoToRestRegistry[entity][constants.DEFAULT_SERIALIZER] = modelSerializer
        else:
            tempSerializer = restifySerializer.createModelSerializers(model, excludedFields, methodFields)
            cfg.djangoToRestRegistry[entity][constants.DEFAULT_SERIALIZER] = tempSerializer
            modelSerializer = customSerializer
        viewSetAttributes =  views.getObjectViewSetAttributes(model, modelSerializer, customViewParams)
        cfg.djangoToRestRegistry[entity][constants.VIEW_SET_ATTRIBUTES] = viewSetAttributes
    
    router1 = routers.DefaultRouter(trailing_slash=True)
    router2 = routers.DefaultRouter(trailing_slash=False)
    for entity in cfg.djangoToRestRegistry:
        model = apps.get_model(entity)
        viewSetAttributes = cfg.djangoToRestRegistry[entity][constants.VIEW_SET_ATTRIBUTES]
        defaultActions = cfg.djangoToRestRegistry[entity].get(constants.DEFAULT_ACTIONS, None)
        if defaultActions is not None:
            for defaultAction in defaultActions:
                if defaultAction[0] == "oneToManyActionFactory":
                    serializer = None
                    customSerializer = cfg.djangoToRestRegistry[defaultAction[2]].get(constants.CUSTOM_SERIALIZER, None)
                    defaultSerializer = cfg.djangoToRestRegistry[defaultAction[2]][constants.DEFAULT_SERIALIZER]
                    if customSerializer is None:
                        serializer = defaultSerializer
                    else:
                        serializer = customSerializer
                    action = views.oneToManyActionFactory(defaultAction[1],serializer,defaultAction[3], defaultAction[4])
                    for x in action:
                        if viewSetAttributes is not None and viewSetAttributes.get(x.__name__, None) is None:
                            viewSetAttributes[x.__name__] = x
                elif defaultAction[0] == "manyToManyActionFactory":
                    action = views.manyToManyActionFactory(defaultAction[1],defaultAction[2],defaultAction[3])
                    for x in action:
                        if viewSetAttributes is not None and viewSetAttributes.get(x.__name__,None) is None:
                            viewSetAttributes[x.__name__] = x
        
        viewSet = type(constants.PROJECT_NAME_PREFIX + entity.replace('.','_') + "ViewSet", (ModelViewSet,), viewSetAttributes)
        cfg.djangoToRestRegistry[entity][constants.DEFAULT_VIEW_SET] = viewSet
        router1.register(prefix=r'{}/{}'.format(relativeUri, model._meta.label.lower().replace('.','/')), viewset=viewSet, basename=model._meta.label.lower().replace('.','_'))
        router2.register(prefix=r'{}/{}'.format(relativeUri, model._meta.label.lower().replace('.','/')), viewset=viewSet, basename=model._meta.label.lower().replace('.','_'))
        
    return router1.urls + router2.urls