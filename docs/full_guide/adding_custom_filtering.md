---
title: Adding custom Filtering
---

!!! Note

    It is advised to go through point 2 of [Marking models to create REST APIs](marking_model_for_REST.md) and [Adding Custom Serializer](adding_custom_serializer.md) and have an understanding of passing custom view attributes.

For filtering, following keys can be used in the dictionary that would be returned from the `getParams()` method of a `ViewParams` class:

* to_rest.constants.FILTER_BACKENDS: To specify filter backends
* to_rest.constants.FILTERSET_FIELDS: To specify filterset fields
* to_rest.constants.SEARCH_FIELDS: To specify search fields
* to_rest.constants.ORDERING_FIELDS: To specify ordering fields
* to_rest.constants.ORDERING: To specify default ordering
* to_rest.constants.FILTERSET_CLASS: To specify filterset class

!!! Note

    If both `to_rest.constants.FILTERSET_CLASS` and `to_rest.constants.FILTERSET_FIELDS` are used then `to_rest.constants.FILTERSET_CLASS` is given preference and `to_rest.constants.FILTERSET_FIELDS` is ignored.

For example, let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomFiltering(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    discipline = models.CharField(max_length=20)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

For above model, various filtering attributes can be provided via a `ViewParams` class. For example:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from to_rest.utils import ViewParams
from rest_framework.filters import SearchFilter, OrderingFilter
from test_basics import filterset # (1)
from django_filters.rest_framework import DjangoFilterBackend

class CustomFiltering(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.FILTER_BACKENDS] = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        temp[constants.FILTERSET_FIELDS] = ['name', 'year', 'discipline']
        temp[constants.SEARCH_FIELDS] = ['name']
        temp[constants.ORDERING_FIELDS] = ['discipline', 'year']
        temp[constants.ORDERING] = ['year']
        return temp
```

1. Here, test_basics is the directory of app

Ensure that the name of the class is passed to the decorator `restifyModel()` in `models.py`. For example:

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

@restifyModel(customViewParams='CustomFiltering')
class StudentWithCustomFiltering(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    discipline = models.CharField(max_length=20)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```