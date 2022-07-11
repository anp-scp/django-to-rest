from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from test_basics_defaults.models import Student
from django.contrib.auth.models import User
from django.test import override_settings
from django.conf import settings
# Create your tests here.

class StudenBasicTestWithDefaultSettings(APITestCase):
    """
    These tests are to make sure that the default tests are picked from settings or not.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics_defaults --settings=tests.settings_test_basics_defaults
    """

    def setUp(self):
        User.objects.create_superuser(username='test', password='test@1234', email=None)
        self.client.credentials(HTTP_AUTHORIZATION="Basic dGVzdDp0ZXN0QDEyMzQ=")
    
    def test_case_list_object(self):
        """
        Test Case: test_basics_defaults-StudenBasicTestWithDefaultSettings-1
        Check if 401 error code is returned if case of no credentials
        """
        url = reverse('test_basics_defaults_student-list')
        self.client.credentials()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_case_filter_object(self):
        """
        Test Case: test_basics_defaults-StudenBasicTestWithDefaultSettings-2
        Ensure that we can filter objects created
        """
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        response = self.client.get(url+"?year=2", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual(datum['year'], 2)
    
    def test_case_search_object(self):
        """
        Test Case: test_basics_defaults-StudenBasicTestWithDefaultSettings-3
        Only 'django_filters.rest_framework.DjangoFilterBackend' is specified in 
        DEFAULT_FILTER_BACKENDS in REST_FRAMEWORK in settings. Ensure that other
        filters like SerachFilter or OrderFilter is not picked up as part of 
        django-to-rest's default behaviour. 
        """
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),3)
        id3 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        response = self.client.get(url+"?search=Doe", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),3)
    
    def test_case_ordering_object(self):
        """
        Test Case: test_basics_defaults-StudenBasicTestWithDefaultSettings-4
        Only 'django_filters.rest_framework.DjangoFilterBackend' is specified in 
        DEFAULT_FILTER_BACKENDS in REST_FRAMEWORK in settings. Ensure that other
        filters like SerachFilter or OrderFilter is not picked up as part of 
        django-to-rest's default behaviour. 
        """
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),3)
        id3 = response.data['id']
        url = reverse('test_basics_defaults_student-list')
        response = self.client.get(url+"?ordering=year,-name", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[2]['name'], 'Ryan Shaw')