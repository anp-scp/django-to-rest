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