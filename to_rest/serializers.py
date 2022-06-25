from rest_framework import serializers

def createModelSerializers(model, excludedFields, methodFields):

    def methodFieldsFactory(methodName):
        def func(self,object):
            temp = eval("object." + methodName + "()")
            return temp
        func.__name__ = "get_" + methodName
        return func

    fields = []
    ##todo create urls for relational fields
    relationalFields = []
    for field in model._meta.get_fields():
        if excludedFields is not None and field.name in excludedFields:
            continue
        elif field.one_to_many or field.many_to_many:
            relationalFields.append(field)
        else:
            fields.append(field.name)
    if methodFields is not None:
        fields.extend(methodFields)
    #create meta attributes for the meta class
    metaAttributes = {}
    metaAttributes["model"] = model
    metaAttributes["fields"] = fields
    metaAttributes["depth"] = 1
    #create meta class for the serializer class
    meta = type("Meta", (object,), metaAttributes)
    #create attributes for serializer class
    serializerAttribute = {}
    serializerAttribute["Meta"] = meta

    if methodFields is not None:
        for methodField in methodFields:
            serializerAttribute[methodField] = serializers.SerializerMethodField(read_only=True)
            serializerAttribute["get_" + methodField] = methodFieldsFactory(methodField)
    
    modelSerializer = type("Restify_" + model.__name__, (serializers.ModelSerializer,), serializerAttribute)
    
    return modelSerializer