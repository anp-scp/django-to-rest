---
title: Adding custom Serializer
---

!!! Note

    It is advised to go through point 2 of [Marking models to create REST APIs](marking_model_for_REST.md)

Let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomSerializer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}, year={}]".format(self.name, self.year)
```

A simple serializer for the model above is given below:

``` py title="serializers.py" linenums="1"
from rest_framework import serializers
from test_basics.models import StudentWithCustomSerializer # (1)

class StudentWithCustomSerializerSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        return StudentWithCustomSerializer.objects.create(**validated_data)
```

1. Here, test_basics is the directory of the app

As mentioned in [Marking models to create REST APIs](marking_model_for_REST.md), all the custom parameters for view needs to be mentioned in a `ViewParams` class and all such class needs to be in module `view_params` in the directory of the app. Let us create a new file in the same working directory called `view_params.py` and create a class as shown below:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from test_basics import serializers # (1)
from to_rest.utils import ViewParams

class CustomSerializer(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer
        return temp
```

1. Here, test_basics is the directory of the app

Note that the dictionary returned by `getParams()` must contain an entry with key `to_rest.constants.SERIALIZER_CLASS`. Now, let us go back to models.py and see how to provide the custom serializer that we created.

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

@restifyModel(customViewParams='CustomSerializer')
class StudentWithCustomSerializer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}, year={}]".format(self.name, self.year)
```

Note the way `CustomSerializer` is passed to the decorator at line 4.