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
    create ModelSerializers for the models, will create viewsets and will hook them with
    routes

    Prameters:
        appName (string): The name of the app to be restified
        relativeUri: (string): The relative url for the api
    Return:
        list of urls (list)
    """

    for entity in cfg.djangoToRestRegistry:
        model = apps.get_app_config(appName).get_model(entity)
        customSerializer = cfg.djangoToRestRegistry[entity][constants.CUSTOM_SERIALIZER]
        customViewParams = cfg.djangoToRestRegistry[entity][constants.CUSTOM_VIEW_PARAMS]
        excludedFields = cfg.djangoToRestRegistry[entity][constants.EXCLUDE_FIELDS]
        methodFields = cfg.djangoToRestRegistry[entity][constants.METHOD_FIELDS]
        searchFields = cfg.djangoToRestRegistry[entity][constants.SEARCH_FIELDS]
        requiredReverseRelFields = cfg.djangoToRestRegistry[entity][constants.REQUIRED_REVERSE_REL_FIELDS]
        modelSerializer = None
        if customSerializer is None:
            modelSerializer = restifySerializer.createModelSerializers(appName, model, excludedFields, methodFields, requiredReverseRelFields)
            cfg.djangoToRestRegistry[entity][constants.DEFAULT_SERIALIZER] = modelSerializer
        else:
            tempSerializer = restifySerializer.createModelSerializers(appName, model, excludedFields, methodFields, requiredReverseRelFields)
            cfg.djangoToRestRegistry[entity][constants.DEFAULT_SERIALIZER] = tempSerializer
            modelSerializer = customSerializer
        viewSetAttributes =  views.getObjectViewSetAttributes(model, modelSerializer, customViewParams)
        cfg.djangoToRestRegistry[entity][constants.VIEW_SET_ATTRIBUTES] = viewSetAttributes
    
    router = routers.DefaultRouter()
    for entity in cfg.djangoToRestRegistry:
        viewSetAttributes = cfg.djangoToRestRegistry[entity][constants.VIEW_SET_ATTRIBUTES]
        customActions = cfg.djangoToRestRegistry[entity][constants.CUSTOM_ACTIONS]
        defaultActions = cfg.djangoToRestRegistry[entity][constants.DEFAULT_ACTIONS]
        if defaultActions is not None:
            for defaultAction in defaultActions:
                if defaultAction[0] == "oneToManyActionFactory":
                    serializer = None
                    customSerializer = cfg.djangoToRestRegistry[defaultAction[2]][constants.CUSTOM_SERIALIZER]
                    defaultSerializer = cfg.djangoToRestRegistry[defaultAction[2]][constants.DEFAULT_SERIALIZER]
                    if customSerializer is None:
                        serializer = defaultSerializer
                    else:
                        serializer = customSerializer
                    action = views.oneToManyActionFactory(defaultAction[1],serializer,defaultAction[3], defaultAction[4])
                    for x in action:
                        if customActions is not None and customActions.get(x.__name__, None) is not None:
                            viewSetAttributes[x.__name__] = customActions[x.__name__]
                            del customActions[x.__name__]
                        else:
                            viewSetAttributes[x.__name__] = x
                elif defaultAction[0] == "manyToManyActionFactory":
                    action = views.manyToManyActionFactory(defaultAction[1],defaultAction[2],defaultAction[3])
                    for x in action:
                        if customActions is not None and customActions.get(x.__name__,None) is not None:
                            viewSetAttributes[x.__name__] = customActions[x.__name__]
                            del customActions[x.__name__]
                        else:
                            viewSetAttributes[x.__name__] = x
        if customActions is not None:
            for customAction in customActions:
                viewSetAttributes[customAction] = customActions[customAction]
        viewSet = type(constants.PROJECT_NAME_PREFIX + entity + "ViewSet", (ModelViewSet,), viewSetAttributes)
        cfg.djangoToRestRegistry[entity][constants.DEFAULT_VIEW_SET] = viewSet
        router.register(prefix=r'{}/{}'.format(relativeUri, entity.lower()), viewset=viewSet, basename=entity.lower())
        
    return router.urls