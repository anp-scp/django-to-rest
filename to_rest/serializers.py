from rest_framework import serializers
from to_rest import constants
from django.urls import reverse
from django.db.models.fields.related import OneToOneField, ForeignKey, ManyToManyField
from django.db.models.fields.reverse_related import OneToOneRel, ManyToOneRel, ManyToManyRel
from to_rest import cfg

def createModelSerializers(appName, model, excludedFields, methodFields, requiredReverseRelFields):

    def methodFieldsFactory(methodName):
        def func(self,object):
            temp = eval("object." + methodName + "()")
            return temp
        func.__name__ = "get_" + methodName
        return func
    
    def relationalMethodFieldsFactory(appName, model, fieldName):
        def func(self,object):
            tempName = model.__name__.lower()
            return(reverse(appName + ":" + tempName + "-" + tempName + "-" + fieldName + "-list", args = [object.pk] ))
        func.__name__ = "get_" + fieldName
        return func

    def addToExtraKwargs(map,fieldName):
        if requiredReverseRelFields is not None and fieldName not in requiredReverseRelFields:
            map[fieldName] = {'required': False}
    
    fields = []
    ##todo create urls for relational fields
    relationalFields = []
    for field in model._meta.get_fields():
        if excludedFields is not None and field.name in excludedFields:
            continue
        elif field.is_relation:
            if cfg.restifyRegistry[field.related_model.__name__] is not None:
                relationalFields.append(field)
        else:
            fields.append(field.name)
    if methodFields is not None:
        fields.extend(methodFields)
    #create meta attributes for the meta class
    metaAttributes = {}
    metaAttributes["model"] = model
    #create meta class for the serializer class
    
    #create attributes for serializer class
    serializerAttribute = {}
    reqFields = dict()
    defaultActions = []
    for relationalField in relationalFields:
        if isinstance(relationalField, OneToOneField):
            fields.append(relationalField.name)
        elif isinstance(relationalField, OneToOneRel):
            temp = relationalField.related_name if relationalField.related_name is not None else relationalField.name
            fields.append(temp)
            addToExtraKwargs(reqFields, temp)
        elif isinstance(relationalField, ForeignKey):
            fields.append(relationalField.name)
        elif isinstance(relationalField, ManyToOneRel):
            temp = relationalField.related_name if relationalField.related_name is not None else relationalField.name + "_set"
            serializerAttribute[temp] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(appName, model, temp)
            fields.append(temp)
            defaultActions.append(("oneToManyActionFactory", model, relationalField.related_model.__name__, relationalField, temp))
        elif isinstance(relationalField, ManyToManyRel):
            temp = relationalField.related_name if relationalField.related_name is not None else relationalField.name + "_set"
            serializerAttribute[temp] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(appName, model, temp)
            fields.append(temp)
            defaultActions.append(("manyToManyActionFactory", model, relationalField,temp)) 
        elif isinstance(relationalField, ManyToManyField):
            temp = relationalField.name
            serializerAttribute[temp] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(appName, model, temp)
            fields.append(temp)
            defaultActions.append(("manyToManyActionFactory", model, relationalField,temp))
    cfg.restifyRegistry[model.__name__][constants.DEFAULT_ACTIONS] = defaultActions
    metaAttributes["fields"] = fields
    metaAttributes["extra_kwargs"] = reqFields
    meta = type("Meta", (object,), metaAttributes)
    serializerAttribute["Meta"] = meta

    if methodFields is not None:
        for methodField in methodFields:
            serializerAttribute[methodField] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_" + methodField] = methodFieldsFactory(methodField)
    
    modelSerializer = type(constants.PROJECT_NAME_PREFIX + model.__name__, (serializers.ModelSerializer,), serializerAttribute)
    
    return modelSerializer