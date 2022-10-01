from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Permission
from test_many_to_one.models import Question1, Choice1
from django.contrib.contenttypes.models import ContentType

class TestCaseCRUD(APITestCase):
    """
    These tests are to ensure that many to one relationship works as expected
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_many_to_one
    """

    def test_case_create_objects_with_defauls(self):
        """
        Test Case: test_many_to_one-TestCaseCRUD-1
        Ensure that objects are created successfully with default values
        """

        url = reverse('test_many_to_one_question-list')
        data = {'question_text': "How is the food?"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        q_id = response.data['id']

        url = reverse('test_many_to_one_question-detail', args=[q_id])
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['pub_date'])

        url = reverse('test_many_to_one_choice-list')
        data = {'choice_text': "Bad", 'question': q_id}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        c_id = response.data['id']

        url = reverse('test_many_to_one_choice-detail', args=[c_id])
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['votes'])
    
    def test_case_one_to_many_list(self):
        """
        Test Case: test_many_to_one-TestCaseCRUD-2
        Ensure that nested URL works correctly for one-to-many
        """
        host = 'http://127.0.0.1:8000'
        url = reverse('test_many_to_one_question-list')
        data = {'question_text': "How is the food?"}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        q_id = response.data['id']
        nestedUrl = response.data['choices']

        c_ids = []
        url = reverse('test_many_to_one_choice-list')
        data = {'choice_text': "Bad", 'question': q_id}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        c_ids.append(response.data['id'])

        data = {'choice_text': "Good", 'question': q_id}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        c_ids.append(response.data['id'])

        data = {'choice_text': "Great", 'question': q_id}
        response = self.client.post(url, data=data, response='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        c_ids.append(response.data['id'])

        url = host + nestedUrl
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for each in response.data:
            self.assertIn(each['id'], c_ids)
        
        # filtering
        url = host + nestedUrl + "?choice_text=Good"
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'],2)

        #search
        url = host + nestedUrl + "?search=Good"
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'],2)

        #ordering
        url = host + nestedUrl + "?ordering=-id"
        response = self.client.get(url, response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], 3)
        self.assertEqual(response.data[1]['id'], 2)
        self.assertEqual(response.data[2]['id'], 1)
        
class TestCaseNestedAccess(APITestCase):
    """
    These tests are to ensure that many to one access policy works as expected
    Command to run these tests:
    $ pwd
    /.../django-to-rest/tests
    $ python3 manage.py test test_many_to_one
    """

    def setUp(self):
        User.objects.create_superuser(username='test', password='test@1234', email=None)
        testy = User.objects.create_user(username='testy', password='test@1234', email=None)
        testify = User.objects.create_user(username='testify', password='test@1234', email=None)

        contentType = ContentType.objects.get_for_model(Question1)
        question1_permissions = Permission.objects.filter(content_type= contentType)
        contentType = ContentType.objects.get_for_model(Choice1)
        choice1_permissions = Permission.objects.filter(content_type= contentType)

        for permission in question1_permissions:
            testy.user_permissions.add(permission)
            testify.user_permissions.remove(permission)
        for permission in choice1_permissions:
            testify.user_permissions.add(permission)
            testy.user_permissions.remove(permission)
        
        q1 = Question1(question_text = "How is the traffic?")
        q1.save()
        c1 = Choice1(choice_text = "Clear for miles", question=q1)
        c1.save()
        c2 = Choice1(choice_text = "Not clear for even a centimetre", question=q1)
        c2.save()

    def test_case_check_access(self):
        """
        Test Case: test_many_to_one-TestCaseNestedAccess-1
        Ensure that objects are accessed as acces policy
        """
        superAdmin = "Basic dGVzdDp0ZXN0QDEyMzQ="
        testy = "Basic dGVzdHk6dGVzdEAxMjM0"
        testify = "Basic dGVzdGlmeTp0ZXN0QDEyMzQ="

        #access by super admin:
        self.client.credentials(HTTP_AUTHORIZATION=superAdmin)
        host = 'http://127.0.0.1:8000'
        url = reverse('test_many_to_one_question1-list')
        response = self.client.get(url,response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        nestedUrl = host + response.data[0]['choices']
        response = self.client.get(nestedUrl, response='json')
        self.assertEqual(len(response.data),2)
        self.client.credentials()

        #access by testy:
        self.client.credentials(HTTP_AUTHORIZATION=testy)
        response = self.client.get(url,response='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        response = self.client.get(nestedUrl, response='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()

        #access by testify:
        self.client.credentials(HTTP_AUTHORIZATION=testify)
        response = self.client.get(url,response='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(nestedUrl, response='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials()
