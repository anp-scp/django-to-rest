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

Many-to-many relationships
------------------------
In case of many-to-many relationships, ``through`` objects for the related objects are returned from the nested url instead of the related objects as ``through`` objects have better information about the relationship.

Nested url for many-to-many relationships support following operations:

* list (GET)
* create (POST)
* retrieve (GET)
* update (PUT)
* partial_update (PATCH)
* delete (DELETE)

All the other view set attributes like `permission_classes`, `filter_backends`, ... applies as provided to the decorator in models.py for the through model.

### Example

Consider the below model:

```py title="models.py" linenums="1"
from django.db import models
from to_rest.decorators import restifyModel

# Create your models here.
@restifyModel
class Student(models.Model):
    name = models.CharField(max_length=75)
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.name
@restifyModel
class Course(models.Model):
    name = models.CharField(max_length=75)
    student = models.ManyToManyField(Student)

    def __str__(self):
        return self.name
```

Consider the following as available data:

    $ http -b --unsorted GET http://127.0.0.1:8000/rest/v1/edu/student/
    [
        {
            "id": 1,
            "name": "John Doe",
            "course_set": "/rest/v1/edu/student/1/course_set/",
            "friends": "/rest/v1/edu/student/1/friends/"
        },
        {
            "id": 2,
            "name": "Eva Doe",
            "course_set": "/rest/v1/edu/student/2/course_set/",
            "friends": "/rest/v1/edu/student/2/friends/"
        },
        {
            "id": 3,
            "name": "Alice Doe",
            "course_set": "/rest/v1/edu/student/3/course_set/",
            "friends": "/rest/v1/edu/student/3/friends/"
        }
    ]

    $ http -b --unsorted GET http://127.0.0.1:8000/rest/v1/edu/course/
    [
        {
            "id": 1,
            "name": "CS601",
            "student": "/rest/v1/edu/course/1/student/"
        },
        {
            "id": 2,
            "name": "CS602",
            "student": "/rest/v1/edu/course/2/student/"
        },
        {
            "id": 3,
            "name": "CS603",
            "student": "/rest/v1/edu/course/3/student/"
        }
    ]

Now, to relate `John Doe` with `CS601` and `CS602`, following can be done:

    $ http -b --unsorted POST http://127.0.0.1:8000/rest/v1/edu/student/1/course_set/ course=1
    {
        "id": 1,
        "course": 1,
        "student": 1
    }
    $ http -b --unsorted POST http://127.0.0.1:8000/rest/v1/edu/student/1/course_set/ course=2
    {
        "id": 2,
        "course": 2,
        "student": 1
    }

In the above example, data for `through` objects are provided. And the relationship between `John Doe` and related courses can be listed as follows:

    $ http -b --unsorted GET http://127.0.0.1:8000/rest/v1/edu/student/1/course_set/
    [
        {
            "id": 1,
            "course": 1,
            "student": 1
        },
        {
            "id": 2,
            "course": 2,
            "student": 1
        }
    ]

Customize nested URL behaviour
------------------------------

To customize the default behaviour of the nested url(s), custom definitions for following method (decorated with the decorator `rest_framework.decorators.action`) needs to be passed as custom view parameters:

* For Many-to-one: 
    - Name of function: `to_rest.constants.ONE_TO_MANY_LIST_ACTION + relatedName`
    - signature: `(self,request,pk=None, *args, **kwargs)`
* For Many-to-many list view: 
    - Name of function: `to_rest.constants.MANY_TO_MANY_LIST_ACTION + relatedName`
    - signature: `(self,request,pk=None, *args,**kwargs)`
* For Many-to-one detail view: 
    - Name of function: `to_rest.constants.MANY_TO_MANY_DETAIL_ACTION + relatedName`
    - signature: `self,request,childPk,pk=None,*args,**kwargs`
    - NOTE: Here `pk` for primary key of the parent object and `childPk` is primar key of the related or nested object

### Example

To customize the behaviour for the example shown for Many-to-many, following can be done:

=== "view_params.py"

    ``` py linenums="1"
    from to_rest import constants
    from to_rest.utils import ViewParams
    from rest_framework.response import Response
    from rest_framework.decorators import action
    from to_rest import constants

    class CustomAction(ViewParams):

        def getParams():
            def customaction(self,request,pk=None, *args,**kwargs):
                if self.request.method == "GET":
                    return Response({'msg':"Custom method working (GET)"})
                elif self.request.method == 'POST':
                    return Response({'msg':"custom method working (POST)"})
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            customaction.__name__ = constants.MANY_TO_MANY_LIST_ACTION + 'course_set'
            customaction = action(detail=True, methods=['get', 'post'], url_path='course_set', url_name="student-course_set-list")(customaction)
            temp = dict()
            temp[constants.MANY_TO_MANY_LIST_ACTION + 'course_set'] = customaction
            return temp
    ```

=== "models.py"

    ```py linenums="1"
    from django.db import models
    from to_rest.decorators import restifyModel

    # Create your models here.
    @restifyModel(customViewParams='CustomAction')
    class Student(models.Model):
        name = models.CharField(max_length=75)
        friends = models.ManyToManyField("self")

        def __str__(self):
            return self.name
    @restifyModel
    class Course(models.Model):
        name = models.CharField(max_length=75)
        student = models.ManyToManyField(Student)

        def __str__(self):
            return self.name
    ```

!!! Note

    * In the above example, `relatedName` is `course_set`.
    * While decorating the method (here at line 18):
        - `url_path` must be in the form (all lower case): 
            - `<relatedName>` for list view
            - `<relatedName>/(?P<childPk>.+)` for detail view
        - `url_name` must be in the form (all lower case): `<parent model name>-<relatedName>-<view type>`
        - View type can be `list` for list view or `detail` for detail view

After making the avobe change, url(s) will work as follows:

    $ http -b GET http://127.0.0.1:8000/rest/v1/edu/student/1/course_set/
    {
        "msg": "Custom method working (GET)"
    }

    $ http -b POST http://127.0.0.1:8000/rest/v1/edu/student/1/course_set/
    {
        "msg": "custom method working (POST)"
    }