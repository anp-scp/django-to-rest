from to_rest import constants
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from to_rest.utils import ViewParams
from rest_framework.authentication import BasicAuthentication

class DDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.update_%(model_name)s'],
        'PATCH': ['%(app_label)s.update_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s']
    }

class CustomPermission(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
        temp[constants.PERMISSION_CLASSES] = [IsAuthenticated, DDjangoModelPermissions]
        return temp