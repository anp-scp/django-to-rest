from to_rest import cfg
from django.apps import apps
from to_rest import constants
from to_rest import serializers as restifySerializer
from to_rest import views
from django.urls import path
from rest_framework.viewsets import ModelViewSet
from rest_framework import routers

def restifyApp(appName, relativeUri):
    """
    The function to restify an app. This will iterate over the models of the appName and will
    create ModelSerializers for the models, will create generic views and will hook them with
    uri(s)

    Prameters:
        appName (string): The name of the app to be restified
        relativeUri: (string): The relative url for the api
    """

    #first: create ModelSerializers for the models
    ## todo: create fields for relations in the serializer
    for entity in cfg.restifyRegistry:
        model = apps.get_app_config(appName).get_model(entity)
        customSerializer = cfg.restifyRegistry[entity][constants.CUSTOM_SERIALIZER]
        customViewParams = cfg.restifyRegistry[entity][constants.CUSTOM_VIEW_PARAMS]
        excludedFields = cfg.restifyRegistry[entity][constants.EXCLUDE_FIELDS]
        methodFields = cfg.restifyRegistry[entity][constants.METHOD_FIELDS]
        searchFields = cfg.restifyRegistry[entity][constants.SEARCH_FIELDS]
        requiredReverseRelFields = cfg.restifyRegistry[entity][constants.REQUIRED_REVERSE_REL_FIELDS]
        modelSerializer = None
        if customSerializer is None:
            modelSerializer = restifySerializer.createModelSerializers(appName, model, excludedFields, methodFields, requiredReverseRelFields)
            cfg.restifyRegistry[entity][constants.DEFAULT_SERIALIZER] = modelSerializer
        else:
            tempSerializer = restifySerializer.createModelSerializers(appName, model, excludedFields, methodFields, requiredReverseRelFields)
            cfg.restifyRegistry[entity][constants.DEFAULT_SERIALIZER] = tempSerializer
            modelSerializer = customSerializer
        viewSetAttributes =  views.getObjectViewSetAttributes(model, modelSerializer, customViewParams)
        cfg.restifyRegistry[entity][constants.VIEW_SET_ATTRIBUTES] = viewSetAttributes
    
    router = routers.DefaultRouter()
    for entity in cfg.restifyRegistry:
        viewSetAttributes = cfg.restifyRegistry[entity][constants.VIEW_SET_ATTRIBUTES]
        customActions = cfg.restifyRegistry[entity][constants.CUSTOM_ACTIONS]
        defaultActions = cfg.restifyRegistry[entity][constants.DEFAULT_ACTIONS]
        if defaultActions is not None:
            for defaultAction in defaultActions:
                if defaultAction[0] == "oneToManyActionFactory":
                    serializer = None
                    customSerializer = cfg.restifyRegistry[defaultAction[2]][constants.CUSTOM_SERIALIZER]
                    defaultSerializer = cfg.restifyRegistry[defaultAction[2]][constants.DEFAULT_SERIALIZER]
                    if customSerializer is None:
                        serializer = defaultSerializer
                    else:
                        serializer = customSerializer
                    action = views.oneToManyActionFactory(defaultAction[1],serializer,defaultAction[3], defaultAction[4])
                    for x in action:
                        if customActions is not None and customActions[x.__name__] is not None:
                            viewSetAttributes[x.__name__] = customActions[x.__name__]
                            del customActions[x.__name__]
                        else:
                            viewSetAttributes[x.__name__] = x
                elif defaultAction[0] == "manyToManyActionFactory":
                    action = views.manyToManyActionFactory(defaultAction[1],defaultAction[2],defaultAction[3])
                    for x in action:
                        if customActions is not None and customActions[x.__name__] is not None:
                            viewSetAttributes[x.__name__] = customActions[x.__name__]
                            del customActions[x.__name__]
                        else:
                            viewSetAttributes[x.__name__] = x
        if customActions is not None:
            for customAction in customActions:
                viewSetAttributes[customAction] = customActions[customAction]
        viewSet = type("Restify_" + entity + "ViewSet", (ModelViewSet,), viewSetAttributes)
        cfg.restifyRegistry[entity][constants.DEFAULT_VIEW_SET] = viewSet
        router.register(prefix=r'{}/{}'.format(relativeUri, entity.lower()), viewset=viewSet, basename=entity.lower())
        
    return router.urls