---
title: Overview
hide:
  - navigation
---
![Django To Rest](img/large_logo_black.png){ width="300"; align=left }

Django To Rest is small tool that helps to expose REST api(s) for
django models with minimum effort. Some of the features are:

* Just add a decorator atop of a model and REST apis is created. That's the work!!!
* Options like filtering and ordering are avilable by default for model fields
* Easy customizations via the decorator itself
* *Summary:* Less time??? Just install the tool and the decorator. Done!!!

* * *
* *Documentation:* [https://anp-scp.github.io/django-to-rest](https://anp-scp.github.io/django-to-rest)
* *Source Code:* [https://github.com/anp-scp/django-to-rest](https://github.com/anp-scp/django-to-rest)
* * *

## Requirements

Django to Rest need following requirements :

* Python 3.8+
* Django 4.0.5
* djangorestframework
* django-filter

* * *

## Installation

Following are the current installation steps

* Download the build `django-to-rest-0.1.tar.gz`
* Go to the directory where the build is located
* Command: `python3 -m pip install django-to-rest-0.1.tar.gz`
* Above command will install all dependencies (except Python itself)

## Example

Let us have a look on an example of how the tool can be used to expose REST API.

Make sure that `djangorestframework` is installed and included in `INSTALLED_APPS ` settings.py as shown below:

    INSTALLED_APPS = [
        'rest_framework',
        'django_filters',
        'polls.apps.PollsConfig',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]

Now create two models as shown below:   `models.py`

    from django.db import models
    from django.utils import timezone
    from django.contrib import admin
    from to_rest.decorators import restifyModel #import the decorator from the library

    # Create your models here.
    @restifyModel #Note the way decorator is used
    class Question(models.Model):
        question_text = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

        def __str__(self):
        return self.question_text


    @restifyModel #Note the way decorator is used
    class Choice(models.Model):
        question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='choices')
        choice_text = models.CharField(max_length=200)
        votes = models.IntegerField(default=0)

        def __str__(self):
            return self.choice_text

Note the use of the decorators. We just need to use the decorator and all the views and serializers would be created during startup. But apart from from that, we need one more line to add in `urls.py` as shown below:

    from to_rest import utils

    app_name = 'polls'
    urlpatterns = [
            ...
            ]
    urlpatterns.extend(utils.restifyApp('polls','rest/v1')) #call this method to add the urls 
    #in url patterns.

That's all. Now start the server.

    `python3 manage,py runserver`
