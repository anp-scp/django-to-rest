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
    * `customViewParams (dict)`: To provide customized methods and variables for view set. For example, custom serializer, list method, create method, retreive method, update method, partial_update method, delete method, get_object methhod, get_queryset, et.
    * `excludeFields (list)`: The fields that needs to be excluded from the JSON object. Provided fields will not be included in the serializer. If customSerializer is provided then this parameter will be ignored.
    * `methodFields (list)`: The list of methods as read only fields. This can be used to include the model's methods output as field. This include only those field that don't take any parameter.
    * `requiredReverseRelFields (list)`: Whenever a one to one relation is created, a reverse field is also included in the serializer for the model in the other side of relationship. To make those a required field in post and put. Provide the list of fields.

For example:

=== "serializers.py"

    ``` py linenums="1"
    from rest_framework import serializers


    class StudentWithCustomSerializerSerializer(serializers.Serializer):

        id = serializers.IntegerField(read_only=True)
        name = serializers.CharField()

        def create(self, validated_data):
            from test_basics.models import StudentWithCustomSerializer # (1)
            return StudentWithCustomSerializer.objects.create(**validated_data)
    ```

    1. using local import to prevernt circular import

=== "view_params.py"

    ``` py linenums="1"
    from to_rest import constants
    from test_basics import serializers

    # Create your views here.
    customViewParams = dict()
    customViewParams[constants.SERIALIZER_CLASS] = serializers.StudentWithCustomSerializerSerializer
    ```

=== "models.py"

    ```py linenums="1"
    from django.db import models
    from to_rest.decorators import restifyModel
    from test_basics.view_params import customViewParams #Here, test_basics is the app directory

    @restifyModel(customViewParams=customViewParams)
    class StudentWithCustomSerializer(models.Model):
        name = models.CharField(max_length=50)
        
        def __str__(self):
            return "[name={}, year={}]".format(self.name, self.year)
    ```



