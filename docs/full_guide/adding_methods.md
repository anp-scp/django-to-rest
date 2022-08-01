---
title: Adding methods
---

## Adding a normal method

Any methods can be added to the view set using a `ViewParams` class. To add a method, an element of dictionary returned by `getParams()` method of the `ViewParams` class should have a key as name of the method (str) and the value should be reference to the function object.

For example, to use custom `list()` method instead of the one given by django-to-rest something similar to below example can be used:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from to_rest.utils import ViewParams
from test_basics import models # Here, test_basics is the app directory

class CustomListMethod(ViewParams):

    def getParams():
        def list(self, request, *args, **kwargs):
            objects = models.StudentWithCustomMethod.objects.filter(year=2)
            serializer = self.get_serializer(objects, many=True)
            return Response(serializer.data)
        temp = dict()
        temp['list'] = list
        return temp
```

!!! Note

    The name of this class needs to be passed to the decorator in `models.py`.

Similarly, any method can be added to the view set.

## Adding a decorated method

Let us consider the following decorated method:

```py title="decorator with no parameters" linenums="1"
@decorator
def function():
    pass
```

The above decorated function is same as:

```py linenums="1"
def function():
    pass
function = decorator(function)
```

Moreover, following decorated method:

```py title="decorater with parameters" linenums="1"
@decorator(param1=abc)
def function():
    pass
```

Above is same as:

```py linenums="1"
def function():
    pass
function = decorator(param1=abc)(function)
```

Hence, to add decorated method, instead of using `@` notation we just need to use the later. Below is an example of adding an action:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from to_rest.utils import ViewParams
from test_basics import models # Here, test_basics is the app directory
from rest_framework.response import Response
from rest_framework.decorators import action

class CustomAction(ViewParams):

    def getParams():
        def customaction(self, request, pk=None):
            obj = models.StudentWithCustomAction.objects.get(pk=pk)
            return Response({'msg':"custom action working for " + obj.name})
        customaction = action(detail=True, methods=['get'], url_name='customaction')(customaction)
        temp = dict()
        temp['customaction'] = customaction
        return temp
```

Note the way the decorator is used at line 13.