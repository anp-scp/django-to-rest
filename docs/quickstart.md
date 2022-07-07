---
title: Quickstart Guide
hide:
  - navigation
---

## **Setup**
Let us start fresh. Ensure that Python 3.8.x is already installed. It is always better to use 
virtual environment to isolate your work with other stuffs. Let us create active a virtual env inside the directory `quickstart`:

    # Create a virtual environment
    $ python3 -m venv qs
    $ source qs/bin/activate

    # Download the package and install it. Installing below will install dependencies like 
    # django, if not already installed
    $ (qs) python3 -m pip install django-to-rest-0.1.tar.gz

    # Create a django project
    $ (qs) django-admin startproject mysite
    $ (qs) cd mysite
    



