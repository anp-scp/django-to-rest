---
title: Marking models to create REST APIs
---

To create REST APIs for a model, first we need to mark the model. And to mark the model, use the decorator `to_rest.decorators.restifyModel`. The decorator can be used in the following two ways:

1. **Without Parameters**: When used without parameters, all the defaults would be applied.
For example:

    ```py title="/.../quickstart/mysite/polls/models.py" linenums="1"
    from django.db import models
    from django.utils import timezone
    from django.contrib import admin
    from to_rest.decorators import restifyModel # (1)

    # Create your models here.
    @restifyModel # (2)
    class Question(models.Model):
        question_text = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

        def __str__(self):
            return self.question_text


    @restifyModel # (3)
    class Choice(models.Model):
        question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='choices')
        choice_text = models.CharField(max_length=200)
        votes = models.IntegerField(default=0)

        def __str__(self):
            return self.choice_text
    ```

    1. Import the decorator from the library
    2. Note the way decorator is used
    3. Note the way decorator is used

2. **With Parameters**: The decorator accepts the following parameters
    * `customViewParams (str)`: This accepts the name of a `ViewParams` class. The `ViewParams` class needs to override the class method `getParams()` to provide customized methods and attributes for view set. For example, custom serializer, list method, create method, retreive method, update method, partial_update method, delete method, get_object method, get_queryset, etc. The `getParams()` method must return a dictionary. 
    * `excludeFields (list)`: The fields that needs to be excluded from the JSON object. Provided fields will not be included in the serializer. If customSerializer is provided then this parameter will be ignored.
    * `methodFields (list)`: The list of methods as read only fields. This can be used to include the model's methods' output as field. This includes only those field that don't take any parameter.

An example of passing custom serializer is given below:

=== "serializers.py"

    ``` py linenums="1"
    from rest_framework import serializers
    from test_basics.models import StudentWithCustomSerializer # (1)

    class StudentWithCustomSerializerSerializer(serializers.Serializer):

        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField()

        def create(self, validated_data):
            return StudentWithCustomSerializer.objects.create(**validated_data)
    ```
    
    1. Here, test_basics is the directory of the app

=== "view_params.py"

    ``` py linenums="1"
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

=== "models.py"

    ```py linenums="1"
    from django.db import models
    from to_rest.decorators import restifyModel

    @restifyModel(customViewParams='CustomSerializer')
    class StudentWithCustomSerializer(models.Model):
        name = models.CharField(max_length=50)
        
        def __str__(self):
            return "[name={}, year={}]".format(self.name, self.year)
    ```
In the above example, a custom serializer has been created in `serializers.py`. A `ViewParams` class, `CustomSerializer` is created in `view_params.py` to provide the custom serializer. And the name of the `ViewParams` class is provided in decorator at line 4 in `models.py`. 

!!! Note

    All `ViewParams` classes must be in the module `view_params` in the directory of the app. That means, in the same location where `models.py` is located.  Django-to-rest will get the name of the `ViewParams` class from the decorator and will search that class in the module `view_params.` Hence, in the example above, `CustomSerializer` is created in `view_params.py`.