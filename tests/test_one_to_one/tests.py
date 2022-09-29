from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from test_one_to_one import models
import json

class TestCaseOneToOne(APITestCase):
    """
    These tests are to ensure that one to one relationship works as expected
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_one_to_one
    """

    def test_case_create_objects(self):
        """
        Test Case: test_one_to_one-TestCaseOneToOne-1
        Ensure that objects are created successfully
        """

        url = reverse('test_one_to_one_student-list')
        data = {'name': "John Doe", 'discipline': "CS", 'program': "MS"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        studentId = response.data['id']
        url = reverse('test_one_to_one_system-list')
        data = {'name': "Dell Vostro 1558", 'location': 'AB1-102', 'student': 1}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    
    
    def test_case_update_objects_null_relation(self):
        """
        Test Case: test_one_to_one-TestCaseOneToOne-2
        Ensure that the OneToOneRel Field is read only and is updated.
        """

        url = reverse('test_one_to_one_system1-list')
        data = {'name': "Dell Vostro 1558", 'location': 'AB1-102'}
        response = self.client.post(url, data=data, response='json')
        systemId1 = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'name': "Dell Vostro 4558", 'location': 'AB1-102'}
        response = self.client.post(url, data=data, response='json')
        systemId2 = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('test_one_to_one_student1-list')
        data = {'name': "John Doe", 'discipline': "CS", 'program': "MS"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        studentId = response.data['id']

        url = reverse('test_one_to_one_student1-detail', args=[studentId])
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['system1'], None)

        url = reverse('test_one_to_one_system1-detail', args=[systemId1])
        data = {'student': studentId}
        response = self.client.patch(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('test_one_to_one_student1-detail', args=[studentId])
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['system1'], systemId1)

        url = reverse('test_one_to_one_system1-detail', args=[systemId1])
        data = json.dumps({'student': None})
        response = self.client.patch(url, data=data, response='json', content_type='application/json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('test_one_to_one_system1-detail', args=[systemId2])
        data = {'student': studentId}
        response = self.client.patch(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('test_one_to_one_student1-detail', args=[studentId])
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['system1'], systemId2)

