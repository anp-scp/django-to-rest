from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from test_basics.models import Student, StudentWithCustomSerializer
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
        self.assertEqual(Student.objects.count(),1)
        id = response.data['id']
        self.assertEqual(Student.objects.get(pk=id).id,id)
        self.assertEqual(Student.objects.get(pk=id).name,'John Doe')
        self.assertEqual(Student.objects.get(pk=id).year,2)
    
    def test_case_partial_update_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-3
        Ensure that we can partially update an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_student-detail', args=[id])
        data = {'name': 'Johny Doe'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(Student.objects.get(pk=id).name, 'Johny Doe')
    
    def test_case_update_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-4
        Ensure that we can update an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
        id = response.data['id']
        url = reverse('test_basics_student-detail', args=[id])
        data = {'name': 'Johny Doe', 'year': 3}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(Student.objects.get(pk=id).name, 'Johny Doe')
        self.assertEqual(Student.objects.get(pk=id).year, 3)
    
    def test_case_delete_object(self):
        """
        Test Case: test_basics-StudentCRUDTest-5
        Ensure that we can delete an object created
        """
        url = reverse('test_basics_student-list')
        data = {'name': 'John Doe', 'year': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),1)
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
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
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
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),3)
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
        self.assertEqual(Student.objects.count(),1)
        id1 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Doe', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),2)
        id2 = response.data['id']
        url = reverse('test_basics_student-list')
        data = {'name': 'Ryan Shaw', 'year': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(),3)
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
    $ python3 manage.py test
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
        self.assertEqual(StudentWithCustomSerializer.objects.count(),1)
        data = {'name': 'Ryan Doe'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentWithCustomSerializer.objects.count(), 2)

        url = reverse('test_basics_studentwithcustomserializer-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[0].get('year', False), False)
        self.assertEqual(response.data[1]['name'], 'Ryan Doe')
        self.assertEqual(response.data[1].get('year', False), False)
