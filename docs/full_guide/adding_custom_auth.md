---
title: Adding custom Authentication class
---

As mentioned earlier, `to_rest.decorators.restifyModel` decorator can also be used with parameters. The custom serializer needs to be passed via the parameter `customViewParams`. Let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomAuthAndPermission(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

Now let us create a new file in the same working directory called `view_params.py` and create the dictionary `customViewParamsCustomAuthAndPermission`:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication

customViewParamsCustomAuthAndPermission = dict()
customViewParamsCustomAuthAndPermission[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
customViewParamsCustomAuthAndPermission[constants.PERMISSION_CLASSES] = [IsAuthenticatedOrReadOnly]
```

Now, let us go back to models.py and see how to provide the authentication classes as viewset attribute.

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel
from test_basics import view_params #Here, test_basics is the app directory

@restifyModel(customViewParams=view_params.customViewParamsCustomAuthAndPermission)
class StudentWithCustomAuthAndPermission(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}]".format(self.name)
```

Note the way `customViewParamsCustomAuthAndPermission` is passed to the decorator at line 5. Since, the authentication classes are part of the dictionary it would be included as the part of corresponding viewset for the model.