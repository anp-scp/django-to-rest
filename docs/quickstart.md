---
title: Quickstart Guide
hide:
  - navigation
---

## **Setup**
Let us start fresh. Ensure that Python 3.8.x is already installed. It is always better to use 
virtual environment to isolate your work with other stuffs. Let us create and activate a virtual env inside the directory `quickstart`:

    # Create a virtual environment
    $ pwd
    /.../quickstart
    $ python3 -m venv qs
    $ source qs/bin/activate

### Installation

    python3 -m pip install django-to-rest

### Creation of a django project and app

    # Create a django project
    $ pwd
    /.../quickstart
    $ (qs) django-admin startproject mysite
    $ (qs) cd mysite
    # create an app in the project
    $ pwd
    /.../quickstart/mysite
    $ (qs) python3 manage.py startapp polls
    $ (qs) python3 manage.py migrate

## **Creation of models**

Now, let us create some models for our polls app. We will create one model named `Question`
and another named `Choice` (This is quite similar to the tutoraial available at django documentation). Here, There will be one-to-many relationship from `Question` to `Choice`.

```py title="/.../quickstart/mysite/polls/models.py" linenums="1"
from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


```
### Activating the app
Now, add the polls app to `INSTALLED_APPS` in `settings.py`. Also add `rest_framework` to it as 
`djang-to-rest` uses `djangorestframework` internally:

```py title="/.../quickstart/mysite/mysite/settings.py" linenums="1"
...
INSTALLED_APPS = [
    'polls',
    'rest_framework',
    ...
]
...
```
After adding the app to `INSTALLED_APPS`, perform migrations for creating required tables in DB.

    $ pwd
    /.../quickstart/mysite
    $ (qs) python3 manage.py makemigrations polls
    $ (qs) python3 manage.py migrate

### Add some data

Since, our app and DB is setup, let us create some dummy data to play with them via REST api.

    $ pwd
    /.../quickstart/mysite
    $ python3 manage.py shell
    Python 3.8.10 (default, Mar 15 2022, 12:22:08) 
    [GCC 9.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from polls.models import Question, Choice
    >>> from django.utils import timezone
    >>> q = Question(question_text="How is the traffic?", pub_date=timezone.now())
    >>> q.save()
    >>> q1 = Question(question_text="What's up?", pub_date=timezone.now())
    >>> q1.save() 
    >>> q.choices.create(choice_text="Conjested", votes=0)
    <Choice: Conjested>
    >>> q.choices.create(choice_text="Clear for miles", votes=0)
    <Choice: Clear for miles>
    >>> q1.choices.create(choice_text="Fine", votes=0)
    <Choice: Fine>
    >>> q1.choices.create(choice_text="Nohing New", votes=0)
    <Choice: Nohing New>

## **Use django-to-rest**

Now as we have some data to play with, let us use `django-to-rest` to create our api. To do that,
we need to mark the models for which the REST apis need to be created. Let us mark our models for
restification!!! (by restification, we mean to create REST api(s) for models):

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


Now, go to projects urls.py and use the following method to get urls for REST apis:

```py title="/.../quickstart/mysite/mysite/urls.py" linenums="1"
from django.contrib import admin
from django.urls import path
from to_rest import utils # (1)

urlpatterns = [
    path('admin/', admin.site.urls),
]
urlpatterns.extend(utils.restifyApp('rest/v1')) # (2)
```

1. Import the utils from to_rest
2. Use the method to get the urls. 'rest/v1' is the prefix for the urls for REST apis


Now go to project's directory and start the server. 

    $ pwd
    /.../quickstart/mysite
    $ python3 manage.py runserver

## **Playing with REST apis**

Now open a new terminal check our apis using httpie:

    $ http --json http://127.0.0.1:8000/
    HTTP/1.1 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Length: 143
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:02:17 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "rest/v1/polls/choice": "http://127.0.0.1:8000/rest/v1/polls/choice/",
        "rest/v1/polls/question": "http://127.0.0.1:8000/rest/v1/polls/question/"
    }

### List objects

    $ http --json http://127.0.0.1:8000/rest/v1/polls/question/
    HTTP/1.1 200 OK
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 262
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:08:56 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choices": "/rest/v1/polls/question/1/choices/",
            "id": 1,
            "pub_date": "2022-07-08T10:02:16.290713Z",
            "question_text": "How is the traffic?"
        },
        {
            "choices": "/rest/v1/polls/question/2/choices/",
            "id": 2,
            "pub_date": "2022-07-08T10:03:15.816192Z",
            "question_text": "What's up?"
        }
    ]

### Retreive object

    $ http --json http://127.0.0.1:8000/rest/v1/polls/question/1/
    HTTP/1.1 200 OK
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    Content-Length: 134
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:11:49 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "choices": "/rest/v1/polls/question/1/choices/",
        "id": 1,
        "pub_date": "2022-07-08T10:02:16.290713Z",
        "question_text": "How is the traffic?"
    }

### List one-to-many objects

    $ http --json http://127.0.0.1:8000/rest/v1/polls/question/1/choices/
    HTTP/1.1 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Length: 123
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:32:31 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choice_text": "Conjested",
            "id": 1,
            "question": 1,
            "votes": 0
        },
        {
            "choice_text": "Clear for miles",
            "id": 2,
            "question": 1,
            "votes": 0
        }
    ]

### Filter using model attributes

    $ http --json http://127.0.0.1:8000/rest/v1/polls/question/1/choices/?choice_text=Conjested
    HTTP/1.1 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Length: 59
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:34:22 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choice_text": "Conjested",
            "id": 1,
            "question": 1,
            "votes": 0
        }
    ]

### Search using model attributes

    $ http --json http://127.0.0.1:8000/rest/v1/polls/question/1/choices/?search=miles
    HTTP/1.1 200 OK
    Allow: GET, HEAD, OPTIONS
    Content-Length: 65
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:36:36 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choice_text": "Clear for miles",
            "id": 2,
            "question": 1,
            "votes": 0
        }
    ]

### Ordering using model attributes

    $ http --json http://127.0.0.1:8000/rest/v1/polls/choice/?ordering=-choice_text
    HTTP/1.1 200 OK
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 235
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 11:52:26 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    [
        {
            "choice_text": "Nohing New",
            "id": 4,
            "question": 2,
            "votes": 0
        },
        {
            "choice_text": "Fine",
            "id": 3,
            "question": 2,
            "votes": 0
        },
        {
            "choice_text": "Conjested",
            "id": 1,
            "question": 1,
            "votes": 0
        },
        {
            "choice_text": "Clear for miles",
            "id": 2,
            "question": 1,
            "votes": 0
        }
    ]


### Partially update (PATCH)

!!! Note

    Here, httpie is used for examples. Hence, JSON like body is not used for PUT, PATCH, POST requests for body. Instead, httpie style is used. Other clients can also be used if any difficulty is faced. 
* * * 
    $ http PATCH http://127.0.0.1:8000/rest/v1/polls/choice/1/ choice_text=Highly\ Conjested
    HTTP/1.1 200 OK
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    Content-Length: 64
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 15:06:21 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "choice_text": "Highly Conjested",
        "id": 1,
        "question": 1,
        "votes": 0
    }

### Create (POST)

    $ http POST http://127.0.0.1:8000/rest/v1/polls/choice/ choice_text=Doing\ bad question=2 votes=0
    HTTP/1.1 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 57
    Content-Type: application/json
    Cross-Origin-Opener-Policy: same-origin
    Date: Fri, 08 Jul 2022 15:19:40 GMT
    Referrer-Policy: same-origin
    Server: WSGIServer/0.2 CPython/3.8.10
    Vary: Accept, Cookie
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY

    {
        "choice_text": "Doing bad",
        "id": 5,
        "question": 2,
        "votes": 0
    }
