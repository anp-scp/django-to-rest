from django.db import models
from .exceptions import DecoratorException
from . import constants
from . import cfg
import logging

def restifyModel(_cls=None, *, customViewParams=None, excludeFields=None, searchFields=None, methodFields=None, customSerialier=None):
    """
    A decorator function to include the models in the registry so that the decorated models
    are marked for restification.

    Parameters:
        _class (object): The class that needs to be decorated.
        excludeGenericApi (list): The api(s) that needs to be excluded or should not be created.
        excludeFields(list): The fields that needs to be excluded from the JSON object. 
        searchFields(list): The fields that can be used for searching. If none, then no serach 
        API is created.
        methodFields(list): The list of methods as read only fields
    Returns:
        decorated class or function object
    """
    
    def decorator_restifyModel(cls):
        """
        The decorator function that does the registry/marking.
        """
        if not issubclass(cls, models.Model):
            raise DecoratorException(constants.NOT_A_MODEL_CLASS_MSG)
        else:
            options = None
            try:
                options = cfg.restifyRegistry[cls.__name__]
            except KeyError:
                logging.info("restify.decorators.restifyModel.decorator_restifyModel:: Performing registration for :" + cls.__name__)
                options = {}
                options[constants.CUSTOM_VIEW_PARAMS] = customViewParams
                options[constants.EXCLUDE_FIELDS] = excludeFields
                options[constants.SEARCH_FIELDS] = searchFields
                options[constants.METHOD_FIELDS] = methodFields
                options[constants.CUSTOM_SERIALIZER] = customSerialier
                cfg.restifyRegistry[cls.__name__] = options
            return cls
    
    if _cls is None:
        return decorator_restifyModel
    else:
        return decorator_restifyModel(_cls)