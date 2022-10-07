---
title: Contributing to django-to-rest
---

Thank you for your interest in contrubiting to this project. Please get involved and help to make the project better. The contributions can be in the form of ideas, development, documentations and testing in the form test scripts.  

Code of Conduct
---------------

Check this link for code of conduct: [Code of Conduct](https://github.com/anp-scp/django-to-rest/blob/master/code_of_conduct.md)

Issues
------

* Ensure that you discuss the topic before raising an issue. Check [Github discussions page](https://github.com/anp-scp/django-to-rest/discussions) for discussions.
* Ensure that the issues are properly explained
* Before raising an issue check if similar issue already exists in [Github issues page](https://github.com/anp-scp/django-to-rest/issues)

Development
-----------

To start developing:

1. Fist create a fork
2. Clone your fork
3. It is recommended to have a virtual environment
4. Install `django 4.0.5`, `django-rest-framework 3.13.1` and `django-filter 22.1`
6. Create new branch
5. Start you development on the new branch...
6. To test your changes in a django project install the project from your local machine using the command: `python3 -m pip install path-to-project's-directory`. For example, if the directory `django-to-rest` is in `~/project/` then the command would be `python3 -m pip install ~/project/django-to-rest/`
7. And then follow the [Quickstart Guide](../quickstart.md) for better understanding. Note that the project needs to be installed from the local machine and not from PyPi.

See [GitHub's Fork a Repo Guide](https://docs.github.com/en/get-started/quickstart/fork-a-repo) for more help.

Testing
-------

!!! Note

    Apart from development, you can also contribute test scripts to cover the scenarios that are not covered yet to make the project better.

There are five apps in the `tests` directory for testing different scenarios:

1. `tests/test_basics`
    - To test generic scenarios
    - Command to run test: 
    ```
    $ python3 manage.py test test_basics
    ```

2. `tests/test_basics_defaults`
    - To test generic scenarios with configuration in settings file
    - For this app there is a dedicated settings file at `tests/tests/settings_test_basics_defaults.py`
    - Command to run test: 
    ```
    $ python3 manage.py test test_basics_defaults --settings=tests.settings_test_basics_defaults
    ```

3. `tests/test_many_to_many`
    - To test scenarios related to many-to-many relationship
    - Command to run test: 
    ```
    $ python3 manage.py test test_many_to_many
    ```

4. `tests/test_many_to_one`
    - To test scenarios related to many-to-one relationship
    - Command to run test: 
    ```
    $ python3 manage.py test test_many_to_one
    ```

5. `tests/test_one_to_one`
    - To test scenarios related to one-to-one relationship
    - Command to run test: 
    ```
    $ python3 manage.py test test_one_to_one
    ```

Before running any test first install django-to-rest by executing below command at the root directory of the repository (where the setup.py resides). This will also install other packages required (that are mentioned in the `Development` section):

    $ python3 -m pip install ./

Whenever any change in code is made, uninstall django-to-rest:

    $ python3 -m pip uninstall django-to-rest

And then install again to run the test on the updated code.
Ensure that the test scripts are well commented so that one can understand about the scenario for which it is tested. Check existing scripts for example.

Documentation
-------------

The documentation is made using [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/). All the files related to documentation is inside `docs` directory. Just update the code and hit below command to preview:

    $ mkdocs serve

Check [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/) for more help.

Contribute and make pull request
-------------

All the contributions have to be made via a pull request. After you have cloned the forked repository, follow below steps:

1. Go into the project's directory (that is `django-to-rest`)
2. Create a new branch using following command in the command line: `git branch new-branch-name`
3. Checkout to the new branch using following command in the command line: `git checkout new-branch-name`
4. Make the changes that you want to contribute
5. Stage your changes using the following command in command line: `git command .`
6. Check the status using the command: `git status`
7. Commit your changes using the command: `git commit -m "commit message"`
8. Push your changes to the remote branch on GitHub by using the following command: `git push -u origin branch_name`
9. Open a pull request directed to our `master` branch

For tutorials on pull request check below links:

* [Github: About pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
* [W3schools: Send Pull Request](https://www.w3schools.com/git/git_remote_send_pull_request.asp?remote=github)