---
title: Adding custom Serializer
---

As mentioned earlier, `to_rest.decorators.restifyModel` decorator can also be used with parameters. The custom serializer needs to be passed via the parameter `customViewParams`. Let us consider the below model:

```py title="models.py" linenums="1"
from django.db import models

class StudentWithCustomSerializer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}, year={}]".format(self.name, self.year)
```

And now let us create a simple serializer for the same.

``` py title="serializers.py" linenums="1"
from rest_framework import serializers

class StudentWithCustomSerializerSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        from test_basics.models import StudentWithCustomSerializer # (1)
        return StudentWithCustomSerializer.objects.create(**validated_data)
```

1. using local import to prevernt circular import

Note that at line 9 in the above code the model `StudentWithCustomSerializer` is imported locally in the method. This is done to prevent circular import issues. Since, we need to provide this custom serializer to the decorator on the model, and if the model here is imported globally then it would be like the model is imported in the models.py itself. Thus, raising the `Import Error` due to circular import issues.

Now let us create a new file in the same working directory called `view_params.py` and create the dictionary `customViewParams`:

``` py title="view_params.py" linenums="1"
from to_rest import constants
from test_basics import serializers

# Create your views here.
customViewParams = dict()
customViewParams[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer
```

Now, let us go back to models.py and see how to provide the custom serializer that we created.

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel
from test_basics.view_params import customViewParams #Here, test_basics is the app directory

@restifyModel(customViewParams=customViewParams)
class StudentWithCustomSerializer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return "[name={}, year={}]".format(self.name, self.year)
```

Note the way `customViewParams` is passed to the decorator at line 5.