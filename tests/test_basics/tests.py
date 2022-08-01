from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from test_basics import models
from django.contrib.auth.models import User
# Create your tests here.

class StudentCRUDTest(APITestCase):
    """
    These tests are for testing basic crud operations.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def test_case_list_students_when_no_object_exists(self):
        """
        Test Case: test_basics-StudentCRUDTest-1
        Ensure that HTTP 204 is returned if no object exists
        """
        url = reverse('test_basics_student-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_case_create_student_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-2
        Ensure that we can create a new student object
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id = response.data['id']
        self.assertEqual(models.Student.objects.get(pk=id).id,id)
        self.assertEqual(models.Student.objects.get(pk=id).name,'John Doe')
        self.assertEqual(models.Student.objects.get(pk=id).year,2)
    
    def test_case_partial_update_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-3
        Ensure that we can partially update an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_student-detail', args=[id])
        data = {'name': 'Johny Doe'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(models.Student.objects.get(pk=id).name, 'Johny Doe')
    
    def test_case_update_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-4
        Ensure that we can update an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_student-detail', args=[id])
        data = {'name': 'Johny Doe', 'year': 3}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(models.Student.objects.get(pk=id).name, 'Johny Doe')
        self.assertEqual(models.Student.objects.get(pk=id).year, 3)
    
    def test_case_delete_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-5
        Ensure that we can delete an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_student-detail', args=[id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        url = reverse('test_basics_student-detail', args=[id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_case_filter_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-6
        Ensure that we can filter objects created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_student-list')
        response = self.client.get(url+"?year=2", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual(datum['year'], 2)
    
    def test_case_search_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-7
        Ensure that we can search objects created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),3)
        id3 = response.data['id']
        url = reverse('test_basics_student-list')
        response = self.client.get(url+"?search=Doe", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual('Doe' in datum['name'], True)
    
    def test_case_ordering_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-8
        Ensure that we can order objects created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Student.objects.count(),3)
        id3 = response.data['id']
        url = reverse('test_basics_student-list')
        response = self.client.get(url+"?ordering=year,-name", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Ryan Shaw')
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[2]['name'], 'John Doe')
    
class StudentCustomSerializer(APITestCase):
    """
    These tests are for testing scenarios for custom serializer.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def test_case_create_list_student_object(self):
        """
        Test Case: test_basics-StudentCustomSerializer-1
        Ensure that we can create a new student object
        """
        url = reverse('test_basics_studentwithcustomserializer-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(),1)
        data = {'name': 'Ryan Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(), 2)

        url = reverse('test_basics_studentwithcustomserializer-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[0].get('year', False), False)
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[1].get('year', False), False)
    
    def test_case_update_student_object(self):
        """
        Test Case: test_basics-StudentCustomSerializer-2
        Ensure that we can update a new student object
        """
        url = reverse('test_basics_studentwithcustomserializer-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomserializer-detail', args=[id])
        data = {'name': 'Ryan Doe'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(), 1)
        self.assertEqual(models.StudentWithCustomSerializer.objects.get(id=id).name, 'Ryan Doe')
    
    def test_case_delete_student_object(self):
        """
        Test Case: test_basics-StudentCustomSerializer-3
        Ensure that we can delete a new student object
        """
        url = reverse('test_basics_studentwithcustomserializer-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomserializer-detail', args=[id])
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.StudentWithCustomSerializer.objects.count(), 0)

class StudentCustomAuthAndPermission(APITestCase):
    """
    These tests are for testing scenarios for custom permission classes and authentication classes.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def setUp(self):
        User.objects.create_superuser(username='test', password='test@1234', email=None)
        self.client.credentials(HTTP_AUTHORIZATION="Basic dGVzdDp0ZXN0QDEyMzQ=")

    def test_case_list_student_object(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-1
        Ensure that we can create a new student object with authentication
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        data = {'name': 'Ryan Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(), 2)

        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[0].get('year', False), False)
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[1].get('year', False), False)
    
    def test_case_update_student_object(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-2
        Ensure that we can update a new student object with authentication
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomauthandpermission-detail', args=[id])
        data = {'name': 'Ryan Doe'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(), 1)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.get(id=id).name, 'Ryan Doe')
    
    def test_case_delete_student_object(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-3
        Ensure that we can delete a new student object with authentication
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomauthandpermission-detail', args=[id])
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(), 0)
    
    def test_case_create_object_without_auth(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-4
        Ensure that we cannot create a new student object without auth
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_case_list_student_object_without_auth(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-5
        Ensure that we can read objects without authentication
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        data = {'name': 'Ryan Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(), 2)

        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        self.client.credentials()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[0].get('year', False), False)
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[1].get('year', False), False)
    
    def test_case_update_student_object_without_auth(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-6
        Ensure that we cannot update an object without auth
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomauthandpermission-detail', args=[id])
        data = {'name': 'Ryan Doe'}
        self.client.credentials()
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.get(id=id).name, 'John Doe')

    def test_case_delete_student_object_without_auth(self):
        """
        Test Case: test_basics-StudentCustomAuthAndPermission-7
        Ensure that we cannot delete student object without authentication
        """
        url = reverse('test_basics_studentwithcustomauthandpermission-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_studentwithcustomauthandpermission-detail', args=[id])
        self.client.credentials()
        response = self.client.delete(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(models.StudentWithCustomAuthAndPermission.objects.count(), 1)

class StudentCustomThrottling(APITestCase):
    """
    These tests are for testing scenarios for custom throttling options as view set attributes.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def test_case_throttling(self):
        """
        Test Case: test_basics-StudentCustomThrottling-1
        Ensure that we cannot hit an api more than 5 times per minute
        """
        url = reverse('test_basics_studentwithcustomthrottling-list')
        data = {'name': 'John Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.StudentWithCustomThrottling.objects.count(),1)
        for i in range(0,4):
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

class StudentCustomFiltering(APITestCase):
    """
    These tests are for testing scenarios for custom filtering options as view set attributes.
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def setUp(self):
        s1 = models.StudentWithCustomFiltering(name="John Doe", year=3, discipline="ME")
        s1.save()
        s2 = models.StudentWithCustomFiltering(name="Ryan Doe", year=2, discipline="CS")
        s2.save()
        s3 = models.StudentWithCustomFiltering(name="Ryan Shaw", year=1, discipline="CS")
        s3.save()
    
    def test_case_default_ordering(self):
        """
        Test Case: test_basics-StudentCustomFiltering-1
        Ensure that the custom default ordering works
        """
        url = reverse('test_basics_studentwithcustomfiltering-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Ryan Shaw')
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[2]['name'], 'John Doe')

    def test_case_filter_object(self):
        """
        Test Case: test_basics-StudentCustomFiltering-2
        Ensure that custom filtering works
        """
        url = reverse('test_basics_studentwithcustomfiltering-list')
        response = self.client.get(url+"?year=1&discipline=CS", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual(datum['year'], 1)
            self.assertEqual(datum['discipline'],'CS')
    
    def test_case_search_object(self):
        """
        Test Case: test_basics-StudentCustomFiltering-3
        Ensure that custom search works
        """
        url = reverse('test_basics_studentwithcustomfiltering-list')
        response = self.client.get(url+"?search=Doe", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual('Doe' in datum['name'], True)
    
    def test_case_ordering_object(self):
        """
        Test Case: test_basics-StudentCustomFiltering-4
        Ensure that custom ordering works
        """
        url = reverse('test_basics_studentwithcustomfiltering-list')
        response = self.client.get(url+"?ordering=discipline,year", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Ryan Shaw')
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[2]['name'], 'John Doe')

class StudentCustomFilterSetVSFilterFields(APITestCase):
    """
    These tests are for ensuring that filterset_class is given higher preference if both filterset_class and filterset_fields
    are present. 
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def setUp(self):
        s1 = models.StudentWithFilterSetClassVSFilterSetField(name="John Doe", year=2, discipline="ME")
        s1.save()
        s2 = models.StudentWithFilterSetClassVSFilterSetField(name="Ryan Doe", year=1, discipline="CS")
        s2.save()

    def test_case_filter_object(self):
        """
        Test Case: test_basics-StudentCustomFilterSetVSFilterFields-1
        Ensure that custom filtering works
        """
        url = reverse('test_basics_studentwithfiltersetclassvsfiltersetfield-list')
        response = self.client.get(url+"?year=1&discipline=CS", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual(datum['year'], 1)
            self.assertEqual(datum['discipline'],'CS')
        response = self.client.get(url+"?name=John Doe", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)

class StudentCustomMethod(APITestCase):
    """
    These tests are for ensuring that custom methods work
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def setUp(self):
        s1 = models.StudentWithCustomMethod(name="John Doe", year=2)
        s1.save()
        s2 = models.StudentWithCustomMethod(name="Ryan Doe", year=1)
        s2.save()
        s3 = models.StudentWithCustomMethod(name="Ryan Shaw", year=2)
        s3.save()

    def test_case_list_object(self):
        """
        Test Case: test_basics-StudentCustomMethod-1
        Ensure that custom filtering works
        """
        url = reverse('test_basics_studentwithcustommethod-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for datum in response.data:
            self.assertEqual(datum['year'], 2)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[1]['name'], 'Ryan Shaw')

class StudentCustomAction(APITestCase):
    """
    These tests are for ensuring that custom actions (specifically, methods with deorators) work
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_basics
    Note: while running these tests all other test apps that are in default settings.py will also run
    """

    def setUp(self):
        s1 = models.StudentWithCustomAction(name="John Doe", year=2)
        s1.save()
        s2 = models.StudentWithCustomAction(name="Ryan Doe", year=1)
        s2.save()

    def test_case_list_object(self):
        """
        Test Case: test_basics-StudentCustomAction-1
        Ensure that custom filtering works
        """
        url = reverse('test_basics_studentwithcustomaction-customaction', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], 'custom action working for John Doe')

        url = reverse('test_basics_studentwithcustomaction-customaction', args=[2])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['msg'], 'custom action working for Ryan Doe')
        