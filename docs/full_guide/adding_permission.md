---
title: Adding Permission class
---

!!! Note

    It is advised to go through point 2 of [Marking models to create REST APIs](marking_model_for_REST.md) and [Adding Custom Serializer](adding_custom_serializer.md) and have an understanding of passing custom view attributes. Here, only example of `view_params` is given.

To add custom permission class, the dictionary returned by `getParams()` method of a `ViewParams` class must have an entry with key `constants.PERMISSION_CLASSES`. For example:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from test_basics import serializers # (1)
from to_rest.utils import ViewParams

class CustomAuthAndPermission(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
        temp[constants.PERMISSION_CLASSES] = [IsAuthenticatedOrReadOnly]
        return temp
```

1. Here, test_basics is the directory of the app

Ensure that the name of the class is passed to the decorator `restifyModel()` in `models.py`. For example:

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

@restifyModel(customViewParams='CustomAuthAndPermission')
class StudentWithCustomAuthAndPermission(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```
