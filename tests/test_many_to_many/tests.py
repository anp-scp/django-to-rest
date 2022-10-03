from unicodedata import name
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Permission
from test_many_to_many.models import Student1, Course1, Student, Course
from django.contrib.contenttypes.models import ContentType

class TestCaseCRUD(APITestCase):
    """
    These tests are to ensure that objects with many to many relationship can be created 
    as expected
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_many_to_many
    """

    def test_case_create_objects(self):
        """
        Test Case: test_many_to_many-TestCaseCRUD-1
        Ensure that objects are created successfully
        """

        url = reverse('test_many_to_many_student-list')
        data = {'name': "John Doe"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'name': "Alice Doe"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('test_many_to_many_course-list')
        data = {'name': "CS601"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'name': "CS602"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
class TestCaseManyToManyRelation(APITestCase):
    """
    These tests are to ensure that many to many relationship works as expected
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_many_to_many
    """

    def setUp(self):
        s1 = Student(name="John Doe")
        s1.save()
        s2 = Student(name="Alice Doe")
        s2.save()
        s3 = Student(name="Eva Doe")
        s3.save()
        c1 = Course(name="CS601")
        c1.save()
        c2 = Course(name="CS602")
        c2.save()

    def test_case_many_to_many_list(self):
        """
        Test Case: test_many_to_many-ManyToManyRelation-1
        Ensure that nested URL works correctly for many-to-many
        """
        host = 'http://127.0.0.1:8000'
        url = reverse('test_many_to_many_student-list')
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        s1_id = response.data[0]['id']
        s1_nestedUrl = response.data[0]['course_set']
        s2_id = response.data[1]['id']
        s2_nestedUrl = response.data[1]['course_set']
        s3_id = response.data[2]['id']
        s3_nestedUrl = response.data[2]['course_set']

        url = reverse('test_many_to_many_course-list')
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c1_id = response.data[0]['id']
        c1_nestedUrl = response.data[0]['student']
        c2_id = response.data[1]['id']
        c2_nestedUrl = response.data[1]['student']

        url = host + s1_nestedUrl
        response = self.client.post(url, data={'course': c1_id}, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rel1_id = response.data['id']

        url = host + s1_nestedUrl + str(rel1_id) + "/"
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student'], s1_id)

        url = host + c1_nestedUrl
        response = self.client.post(url, data={'student': s2_id}, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = host + c1_nestedUrl + "?ordering=student"
        response = self.client.get(url, response = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['student'], s1_id)
        self.assertEqual(response.data[1]['student'], s2_id)

        url = host + c2_nestedUrl
        response = self.client.post(url, data={'student': s1_id}, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rel2_id = response.data['id']

        url = host + s1_nestedUrl + "?ordering=course"
        response = self.client.get(url, response = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['course'], c1_id)
        self.assertEqual(response.data[1]['course'], c2_id)
        self.assertEqual(len(response.data),2)

        url = host + c2_nestedUrl + "?ordering=student"
        response = self.client.get(url, response = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)

        url = host + c2_nestedUrl + str(rel2_id) + "/"
        response = self.client.patch(url, data={'student': s2_id}, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = host + s1_nestedUrl + "?ordering=course"
        response = self.client.get(url, response = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)

        url = host + c1_nestedUrl + str(rel1_id) + "/"
        response = self.client.patch(url, data={'student': s3_id}, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = host + s1_nestedUrl + "?ordering=course"
        response = self.client.get(url, response = 'json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = host + s3_nestedUrl + str(rel1_id) + "/"
        response = self.client.delete(url,response='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = host + s3_nestedUrl
        response = self.client.get(url,response='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
