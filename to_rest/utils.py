from . import cfg
from django.apps import apps
from . import constants
from . import serializers as restifySerializer
from rest_framework import serializers
from . import views
from django.urls import path

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
    paths = []
    for entity in cfg.restifyRegistry:
        model = apps.get_app_config(appName).get_model(entity)
        customSerializer = cfg.restifyRegistry[entity][constants.CUSTOM_SERIALIZER]
        customViewParams = cfg.restifyRegistry[entity][constants.CUSTOM_VIEW_PARAMS]
        excludedFields = cfg.restifyRegistry[entity][constants.EXCLUDE_FIELDS]
        methodFields = cfg.restifyRegistry[entity][constants.METHOD_FIELDS]
        searchFields = cfg.restifyRegistry[entity][constants.SEARCH_FIELDS]
        modelSerializer = None
        if customSerializer is None:
            modelSerializer = restifySerializer.createModelSerializers(model, excludedFields, methodFields)
        else:
            modelSerializer = customSerializer
        ObjectListView =  views.createObjectListView(model, modelSerializer, customViewParams)
        ObjectDetailView =  views.createObjectDetailView(model, modelSerializer, customViewParams)

        paths.append(path(relativeUri + "/" + model.__name__.lower(), ObjectListView.as_view()))
        paths.append(path(relativeUri + "/" + model.__name__.lower() + "/<int:pk>", ObjectDetailView.as_view()))
        
    return paths