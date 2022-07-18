from to_rest import constants
from test_basics import serializers

# Create your views here.
customViewParams = dict()
customViewParams[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer