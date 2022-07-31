---
title: Adding throttling options
---

!!! Note

    It is advised to go through point 2 of [Marking models to create REST APIs](marking_model_for_REST.md) and [Adding Custom Serializer](adding_custom_serializer.md) and have an understanding of passing custom view attributes.

Here, an example of [ScopedRateThrottle](https://www.django-rest-framework.org/api-guide/throttling/#scopedratethrottle) class is given as other types of classes and options can be managed solely via `settings.py`.

Let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomThrottling(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

To add throttling class, the dictionary returned by `getParams()` method of a `ViewParams` class must have an entry with key `constants.THROTTLE_SCOPE`. For example:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from to_rest.utils import ViewParams

class CustomThrottling(ViewParams):

    def getParams():
        temp = dict()
        temp[constants.THROTTLE_SCOPE] = "studentCustomThrottle"
        return temp
```

Now, let us go back to models.py and see how to provide the throttle scope as viewset attribute.

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

@restifyModel(customViewParams='CustomThrottling')
class StudentWithCustomThrottling(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

Also, ensure that throttle class and other options are specified in `settings.py`:

```py title="settings.py" linenums="1"
...
REST_FRAMEWORK = {
    ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'studentCustomThrottle': '5/min'
    }
    ...
}
```