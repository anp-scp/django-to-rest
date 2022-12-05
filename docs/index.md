---
title: Overview
hide:
  - navigation
---
![Django To Rest](img/large_logo_black.png){ width="300"; align=left }

Django To Rest is small tool that helps to expose REST api(s) for
django models with minimum effort. This utility is for one who uses `Django REST Framework` for writing REST APIs. The tool enables you to focus only on the code needed explicitly. The tool handles all boilerplate for writing CRUD APIs. Some of the features are:

* Just add a decorator at top of a model and REST api(s) are created. That's the work!!!
* Options like filtering and ordering are avilable by default for model fields
* Easy customisations via the decorator itself
* *Summary:* Less time??? Just install the tool and use the decorator. Done!!!

* * *
* *Documentation:* [https://anp-scp.github.io/django-to-rest](https://anp-scp.github.io/django-to-rest)
* *Source Code:* [https://github.com/anp-scp/django-to-rest](https://github.com/anp-scp/django-to-rest)
* * *

## **Requirements**

Django to Rest need following requirements :

* Python 3.8+
* Django 4.0.5+
* djangorestframework 3.13.1+
* django-filter 22.1

* * *

## **Installation**

django-to-rest is published as a package and can be installed using pip. Install with (consider creating a virtual environment):

    python3 -m pip install django-to-rest

## **Example**

Let us have a look on an example of how the tool can be used to expose REST API.

Let us assume that the following are the requirements:

1. A polls app having certain questions and each question have some choices.
2. All CRUD URLs for question and choice objects.
3. We need an URL which simply increments a counter

Make sure that `djangorestframework` is installed and included in `INSTALLED_APPS ` in settings.py as shown below:
```py title="settings.py" linenums="1"
...
INSTALLED_APPS = [
    'rest_framework',
    ...
]
...
```
Now create two models as shown below:
```py title="models.py" linenums="1"
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

Note the use of the decorators. We just need to use the decorator and all the views and serializers would be created during startup. But apart from that, we need one more line to add in `urls.py` of the project (not any app) as shown below:
```py title="urls.py" linenums="1"
from django.urls import path
from to_rest import utils
from django.http import JsonResponse

urlpatterns = [
        ...
        ]
urlpatterns.extend(utils.restifyApp('rest/v1')) # (1)
```

1. call this method to add the urls in url patterns. Here the parameter 'rest/v1' is the prefix to be used in the url.

That's all. All the above configurations will create the CRUD APIs for the classes that we marked using the decorator. For the 3rd requirement we can simply write a method the way we write in `Django` or `Django REST Framework`. We add the following lines in `urls.py`:

```py
count = 0 

def counter(request) :
    global count
    if request.method == 'GET':
        count += 1
        return JsonResponse({'count': count})
urlpatterns.append(path('count/', counter))
```

Now start the server. We add some data and check the dev url `http://127.0.0.1:8000/`. Below is an example with httpie:

    $ http -b --unsorted http://127.0.0.1:8000/
    {
        "rest/v1/polls/question": "http://127.0.0.1:8000/rest/v1/polls/question",
        "rest/v1/polls/choice": "http://127.0.0.1:8000/rest/v1/polls/choice"
    }

    $ http -b --unsorted http://127.0.0.1:8000/rest/v1/polls/question
    [
        {
            "id": 1,
            "question_text": "How is the traffic?",
            "pub_date": "2022-07-08T10:02:16.290713Z",
            "choices": "/rest/v1/polls/question/1/choices"
        },
        {
            "id": 2,
            "question_text": "What's up?",
            "pub_date": "2022-07-08T10:03:15.816192Z",
            "choices": "/rest/v1/polls/question/2/choices"
        }
    ]

    $ http -b --unsorted http://127.0.0.1:8000/rest/v1/polls/question/1/choices
    [
        {
            "id": 1,
            "choice_text": "Highly Conjested",
            "votes": 0,
            "question": 1
        },
        {
            "id": 2,
            "choice_text": "Clear for miles",
            "votes": 0,
            "question": 1
        }
    ]

    $ http -b --unsorted http://127.0.0.1:8000/count/
    {
        "count": 1
    }

    $ http -b --unsorted http://127.0.0.1:8000/count/
    {
        "count": 2
    }

    $ http -b --unsorted http://127.0.0.1:8000/count/
    {
        "count": 3
    }

Here, we wrote extra code only for the `/count/` URL and other CRUD URLs where created by the utility.

## **Quickstart**

The [quick start guide](quickstart.md) is a short tutorial which is the fastest way to get everything setup and get an overview of the tool.

## **Contributing**

Check the [contribution guidelines](community/contributing_to_django_to_rest.md) to know about how to contribute to the project.