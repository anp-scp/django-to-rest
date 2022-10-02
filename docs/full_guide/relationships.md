---
title: Relationship
---

One-to-one relationships
------------------------
This section shows the behaviour for one to one relationship:

Consider following models:

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Student(models.Model):
    name = models.CharField(max_length=75)
    discipline = models.CharField(max_length=10)
    program = models.CharField(max_length=10)

    def __str__(self):
        return "[name={} ; discipline={} ; program={}]".format(self.name, self.discipline, self.program)

@restifyModel
class System(models.Model):
    name = models.CharField(max_length=75)
    location = models.CharField(max_length=20)
    student = models.OneToOneField(Student, models.CASCADE, null=True)

    def __str__(self):
        return "[name={} ; location={}]".format(self.name, self.location)

```

In the above models, there is a one-to-one relationship from System1 to Student1. Let us create a student object:

    $ http POST http://127.0.0.1:8000/rest/v1/lab/student/ name=John\ Doe discipline=CS program=MS
    HTTP/1.1 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 73
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 30 Sep 2022 09:47:29 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.10.6
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "discipline": "CS",
        "id": 1,
        "name": "John Doe",
        "program": "MS",
        "system": null
    }

Here, the student object has got an attribute, "system" which is null as this student object is not yet mapped with any system object. This attribute is a field of type `OneToOneRel` and not of type `OneToOneField`. Thus, this is a read-only field. This field will get some value when this object is mapped with a System object. Let us create a system object:

    $ http POST http://127.0.0.1:8000/rest/v1/lab/system/ name=Dell\ Vostro\ 1558 location=AB1-102
    HTTP/1.1 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 70
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 30 Sep 2022 11:27:53 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.10.6
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "id": 1,
        "location": "AB1-102",
        "name": "Dell Vostro 1558",
        "student": null
    }

!!! Note

    In the model, the `null` flag for the `OneToOneField` is set as `True`. Not allowing null values may have restrictions on updating relations.

The "student" attribute here is `OneToOneField` and is read-write. Now, this object can be used to map "Student" and "System" object as shown below:

    $ http PATCH http://127.0.0.1:8000/rest/v1/lab/system/1/ student=1
    HTTP/1.1 200 OK
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    Content-Length: 67
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 30 Sep 2022 20:11:52 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.10.6
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "id": 1,
        "location": "AB1-102",
        "name": "Dell Vostro 1558",
        "student": 1
    }

    $ http PATCH http://127.0.0.1:8000/rest/v1/lab/student/1/
    HTTP/1.1 200 OK
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    Content-Length: 70
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 30 Sep 2022 20:12:47 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.10.6
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "discipline": "CS",
        "id": 1,
        "name": "John Doe",
        "program": "MS",
        "system": 1
    }

Notice that the student object now shows primary key of related "System" object.

Many-to-one relationships
------------------------
This section shows the behaviour for many to one relationship:

Consider the following model:

```py title="models.py" linenums="1"
from django.db import models
from django.utils import timezone
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def pub_date_default():
        return timezone.now()

    pub_date = models.DateTimeField('date published', default=pub_date_default)

@restifyModel
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

In the above models there is a many-to-one relationship from `Choice` to `Question`. This will create a read only field called `choices` which will have link for the related `choices` object. For example:

    $ http GET http://127.0.0.1:8000/rest/v1/polls/question/
    HTTP/1.1 200 OK
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 136
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Sun, 02 Oct 2022 09:30:42 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.10.6
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choices": "/rest/v1/polls/question/1/choices/",
            "id": 1,
            "pub_date": "2022-10-02T09:23:28.297936Z",
            "question_text": "How is the traffic?"
        }
    ]


On fetching the link for choices we get all the related `Choice`  object:

    $ http -b GET http://127.0.0.1:8000/rest/v1/polls/question/1/choices/
    [
        {
            "choice_text": "Clear for miles...",
            "id": 1,
            "question": 1,
            "votes": 0
        },
        {
            "choice_text": "Stuck for an hour",
            "id": 2,
            "question": 1,
            "votes": 0
        }
    ]

!!! Note

    This url is only for list operations as all the other operations like create, update and delete can be done from the other side of the relationship.

All the other view set attributes like `permission_classes`, `filter_backends`, ... applies as provided to the decorator in models.py. For example conside following `models` and `view_params`:

=== "view_params.py"

    ``` py linenums="1"
    from to_rest import constants
    from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
    from to_rest.utils import ViewParams
    from rest_framework.authentication import BasicAuthentication

    class DDjangoModelPermissions(DjangoModelPermissions):
        perms_map = {
            'GET': ['%(app_label)s.view_%(model_name)s'],
            'POST': ['%(app_label)s.add_%(model_name)s'],
            'PUT': ['%(app_label)s.update_%(model_name)s'],
            'PATCH': ['%(app_label)s.update_%(model_name)s'],
            'DELETE': ['%(app_label)s.delete_%(model_name)s']
        }

    class CustomPermission(ViewParams):

        def getParams():
            temp = dict()
            temp[constants.AUTHENTICATION_CLASSES] = [BasicAuthentication]
            temp[constants.PERMISSION_CLASSES] = [IsAuthenticated, DDjangoModelPermissions]
            return temp
    ```

=== "models.py"

    ```py linenums="1"
    from django.db import models
    from django.utils import timezone
    from to_rest.decorators import restifyModel

    # Create your models here.
    @restifyModel(customViewParams='CustomPermission')
    class Question1(models.Model):
        question_text = models.CharField(max_length=200)

        def pub_date_default():
            return timezone.now()

        pub_date = models.DateTimeField('date published', default=pub_date_default)

    @restifyModel(customViewParams='CustomPermission')
    class Choice1(models.Model):
        question = models.ForeignKey(Question1, on_delete=models.CASCADE, related_name='choices')
        choice_text = models.CharField(max_length=200)
        votes = models.IntegerField(default=0)
    ```

Now, if a user has all permissions for `Question1` and not for `Choice1` then the user can access the url(s) for `Question1` but not the nested url for related `Choice1` objects:

    $ http -b -a testy:test@1234 GET http://127.0.0.1:8000/rest/v1/polls/question1/
    [
        {
            "choices": "/rest/v1/polls/question1/1/choices/",
            "id": 1,
            "pub_date": "2022-10-02T09:23:47.805702Z",
            "question_text": "How is the traffic?"
        }
    ]

    $ http -b -a testy:test@1234 GET http://127.0.0.1:8000/rest/v1/polls/question1/1/choices/
    {
        "detail": "You do not have permission to perform this action."
    }