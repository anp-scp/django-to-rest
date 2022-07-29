---
title: Adding custom throttling options
---

Here, an example of [ScopedRateThrottle](https://www.django-rest-framework.org/api-guide/throttling/#scopedratethrottle) class is given as other types of classes and options can be managed solely via `settings.py`.

Let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomThrottling(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

Now let us create a new file in the same working directory called `view_params.py` and create the dictionary `customViewParamsCustomThrottling`:

``` py title="view_params.py" linenums="1"
from to_rest import constants

customViewParamsCustomThrottling = dict()
customViewParamsCustomThrottling[constants.THROTTLE_SCOPE] = "studentCustomThrottle"
```

Now, let us go back to models.py and see how to provide the throttle scope as viewset attribute.

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel
from test_basics import view_params #Here, test_basics is the app directory

@restifyModel(customViewParams=view_params.customViewParamsCustomThrottling)
class StudentWithCustomThrottling(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

Note the way `customViewParamsCustomThrottling` is passed to the decorator at line 5. Since, the throttle scope is part of the dictionary it would be included as the part of corresponding viewset for the model.

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