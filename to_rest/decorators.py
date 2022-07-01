from django.db import models
from to_rest import exceptions
from to_rest import constants
from to_rest import cfg
from rest_framework.serializers import BaseSerializer
import logging
from collections import defaultdict

def restifyModel(_cls=None, *, customViewParams=None, excludeFields=None, searchFields=None, methodFields=None, customSerialier=None, requiredReverseRelFields=None, customActions=None):
    """
    A decorator function to include the models in the registry so that the decorated models
    are marked for restification. By restification we mean to expose REST api(s) for that 
    model.

    Parameters:
        _cls (object): The class that needs to be decorated.

        customViewParams (dict): To provide customize methods for view set. For example, for
        list, create, retreive, update, partial_update, delete, get_object and get_queryset.

        excludeFields (list): The fields that needs to be excluded from the JSON object. provide
        fields will not be included in the serializer. If customSerializer is provided then this
        parameter will ne ignored. 

        searchFields (list): The fields that can be used for searching via query params. If none, 
        then no serach query params would be supported.

        methodFields (list): The list of methods as read only fields. This can be used to include the
        model's methods output as field. This include only those field that don't take any parameter.

        customSerialier (Serializer): To provide custom serializer

        requiredReverseRelFields (list): Whenever a one to one relation is created,
        a reverse field is also included in the serializer for the model in the other side of relationship.
        To make those a required field in post and put. Use this parameter.

        customActions (dict): To provide extra actions on viewset
    Returns:
        decorated class or function object
    """
    if customViewParams is not None and isinstance(customViewParams, dict):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("customViewParams", "dict", type(customViewParams)))
    if customViewParams is not None and isinstance(excludeFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("excludeFields", "list", type(excludeFields)))
    if customViewParams is not None and isinstance(searchFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("searchFields", "list", type(searchFields)))
    if customViewParams is not None and isinstance(methodFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("methodFields", "list", type(methodFields)))
    if customViewParams is not None and isinstance(customSerialier, BaseSerializer):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("customSerialier", "BaseSerializer", type(customSerialier)))
    if customViewParams is not None and isinstance(requiredReverseRelFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("requiredReverseRelFields", "list", type(requiredReverseRelFields)))
    if customViewParams is not None and isinstance(customActions, dict):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("customActions", "dict", type(customActions)))
    def decorator_restifyModel(cls):
        """
        The decorator function that does the registry/marking.
        """
        if not issubclass(cls, models.Model):
            raise exceptions.DecoratorException(constants.NOT_A_MODEL_CLASS_MSG)
        else:
            options = None
            try:
                options = cfg.djangoToRestRegistry[cls.__name__]
            except KeyError:
                logging.info("todjango.decorators.restifyModel.decorator_restifyModel:: Performing registration for :" + cls.__name__)
                options = defaultdict(None)
                options[constants.CUSTOM_VIEW_PARAMS] = customViewParams
                options[constants.EXCLUDE_FIELDS] = excludeFields
                options[constants.SEARCH_FIELDS] = searchFields
                options[constants.METHOD_FIELDS] = methodFields
                options[constants.CUSTOM_SERIALIZER] = customSerialier
                options[constants.REQUIRED_REVERSE_REL_FIELDS] = requiredReverseRelFields
                options[constants.CUSTOM_ACTIONS] = customActions
                cfg.djangoToRestRegistry[cls.__name__] = options
            return cls
    
    if _cls is None:
        return decorator_restifyModel
    else:
        return decorator_restifyModel(_cls)