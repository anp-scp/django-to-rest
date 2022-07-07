from rest_framework import serializers
from to_rest import constants
from django.urls import reverse
from django.db.models.fields.related import OneToOneField, ForeignKey, ManyToManyField
from django.db.models.fields.reverse_related import OneToOneRel, ManyToOneRel, ManyToManyRel
from to_rest import cfg

def createModelSerializers(model, excludedFields, methodFields, requiredReverseRelFields):
    """
    Method to create model serializers for the models marked for restification.

    Parameters:

        model (django.db.models.Model): The model itself

        excludedFields (list): The list of fields to be excluded

        requiredReverseRelFields (list): One to One reverse fields to be made required.  

    Returns:

        serializer (rest_framework.serializers.ModelSerializer)
    """

    def methodFieldsFactory(methodName):
        """
        Method to create seriaizer method for additional method fields

        Parameters:

            methodName (str): name of the method field

        Returns:

            func object
        """
        def func(self,object):
            temp = eval("object." + methodName + "()")
            return temp
        func.__name__ = "get_" + methodName
        return func
    
    def relationalMethodFieldsFactory(model, fieldName):
        """
        Method to create a serializer method for creating a url for the relational fields
        in case of one to many and many to many relation

        Parameters:

            model (django.db.models.Model): model for which the serializer method is created.

            fieldName (str): Name of the relational field

        Returns:

            func object
        """
        def func(self,object):
            tempName = model.__name__.lower()
            return(reverse(model._meta.label.lower().replace('.','_') + "-" + tempName + "-" + fieldName + "-list", args = [object.pk] ))
        func.__name__ = "get_" + fieldName
        return func

    def addToExtraKwargs(map,fieldName):
        if requiredReverseRelFields is not None and fieldName not in requiredReverseRelFields:
            map[fieldName] = {'required': False}
    
    fields = []
    relationalFields = []
    for field in model._meta.get_fields():
        if excludedFields is not None and field.name in excludedFields:
            continue
        elif field.is_relation:
            if cfg.djangoToRestRegistry[field.related_model._meta.label] is not None:
                relationalFields.append(field)
        else:
            fields.append(field.name)
    if methodFields is not None:
        fields.extend(methodFields)
    #create meta attributes for the meta class
    metaAttributes = {}
    metaAttributes["model"] = model
    
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
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(model, temp)
            fields.append(temp)
            defaultActions.append(("oneToManyActionFactory", model, relationalField.related_model._meta.label, relationalField, temp))
        elif isinstance(relationalField, ManyToManyRel):
            temp = relationalField.related_name if relationalField.related_name is not None else relationalField.name + "_set"
            serializerAttribute[temp] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(model, temp)
            fields.append(temp)
            defaultActions.append(("manyToManyActionFactory", model, relationalField,temp)) 
        elif isinstance(relationalField, ManyToManyField):
            temp = relationalField.name
            serializerAttribute[temp] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_"+temp] = relationalMethodFieldsFactory(model, temp)
            fields.append(temp)
            defaultActions.append(("manyToManyActionFactory", model, relationalField,temp))
            #in the above if conditions, certain tuples are added to defaultActions to create
            #corresponding action for the one to many and many to many fields
    cfg.djangoToRestRegistry[model._meta.label][constants.DEFAULT_ACTIONS] = defaultActions
    metaAttributes["fields"] = fields
    metaAttributes["extra_kwargs"] = reqFields
    meta = type("Meta", (object,), metaAttributes)
    serializerAttribute["Meta"] = meta #create meta class for the serializer class

    if methodFields is not None:
        for methodField in methodFields:
            serializerAttribute[methodField] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_" + methodField] = methodFieldsFactory(methodField)
    
    modelSerializer = type(constants.PROJECT_NAME_PREFIX + model._meta.label.replace('.','_'), (serializers.ModelSerializer,), serializerAttribute)
    
    return modelSerializer