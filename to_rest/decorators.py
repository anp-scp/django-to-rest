from django.db import models
from to_rest import exceptions
from to_rest import constants
from to_rest import cfg
from rest_framework.serializers import BaseSerializer
import logging
from collections import defaultdict

def restifyModel(_cls=None, *, customViewParams=None, excludeFields=None, methodFields=None):
    """
    A decorator function to include the models in the registry so that the decorated models
    are marked for restification. By restification we mean to expose REST api(s) for that 
    model.

    Parameters:
        _cls (object): The class that needs to be decorated.

        customViewParams (str): To provide class names in view_params.py for custom view parameters.

        excludeFields (list): The fields that needs to be excluded from the JSON object. provide
        fields will not be included in the serializer. If customSerializer is provided then this
        parameter will ne ignored. 

        methodFields (list): The list of methods as read only fields. This can be used to include the
        model's methods output as field. This include only those field that don't take any parameter.

    Returns:
        decorated class or function object
    """
    if customViewParams is not None and not isinstance(customViewParams, str):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("customViewParams", "str", type(customViewParams)))
    if excludeFields is not None and not isinstance(excludeFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("excludeFields", "list", type(excludeFields)))
    if methodFields is not None and not isinstance(methodFields, list):
        raise TypeError(constants.TYPE_ERROR_MESSAGE.format("methodFields", "list", type(methodFields)))
    def decorator_restifyModel(cls):
        """
        The decorator function that does the registry/marking.
        """
        if not issubclass(cls, models.Model):
            raise exceptions.DecoratorException(constants.NOT_A_MODEL_CLASS_MSG)
        else:
            options = None
            try:
                options = cfg.djangoToRestRegistry[cls._meta.label]
            except KeyError:
                logging.info("todjango.decorators.restifyModel.decorator_restifyModel:: Performing registration for :" + cls.__name__)
                options = defaultdict(None)
                options[constants.CUSTOM_VIEW_PARAMS] = customViewParams
                options[constants.EXCLUDE_FIELDS] = excludeFields
                options[constants.METHOD_FIELDS] = methodFields
                #options[constants.CUSTOM_SERIALIZER] = None if customViewParams is None else customViewParams.pop(constants.SERIALIZER_CLASS, None)
                cfg.djangoToRestRegistry[cls._meta.label] = options
            return cls
    
    if _cls is None:
        return decorator_restifyModel
    else:
        return decorator_restifyModel(_cls)