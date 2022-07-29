from to_rest import constants
from test_basics import serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication

customViewParamsCustomSerializer = dict()
customViewParamsCustomSerializer[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer

customViewParamsCustomAuthAndPermission = dict()
customViewParamsCustomAuthAndPermission[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
customViewParamsCustomAuthAndPermission[constants.PERMISSION_CLASSES] = [IsAuthenticatedOrReadOnly]

customViewParamsCustomThrottling = dict()
customViewParamsCustomThrottling[constants.THROTTLE_SCOPE] = "studentCustomThrottle"