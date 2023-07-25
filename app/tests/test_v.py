from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from app.models import Snippet
c = APIClient()


class GetListUsersTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='TestUser1',
                            email='test@tset.test')
        user.set_password('1234567890')
        user.save()

    def test_get_user_list(self):
        response = c.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_count_users(self):
        response = c.get('/users/')
        self.assertEqual(response.json()['count'], 1)

    def test_user_details(self):
        response = c.get('/users/')
        self.assertContains(response, 'TestUser1')
        self.assertEqual(len(response.json()['results'][0]['snippets']), 0)


class GetListSnippetsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create(username='User1')
        user1.set_password('1234567890')
        user1.save()

        user2 = User.objects.create(username='User2')
        user2.set_password('12345678901')
        user2.save()

        Snippet.objects.create(title='test title1',
                               linenos=True,
                               code='Code1',
                               owner_id=user1.id
                               )
        Snippet.objects.create(code='Code2', owner_id=user2.id)

    def test_check_url_unauthorized_user(self):
        response = c.get('/snippets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_snippets_unauthorized_user(self):
        response = c.get('/snippets/')
        self.assertEqual(response.json()['count'], 2)

    def test_get_list_snippets_authorized_user(self):
        response = c.get('/snippets/')
        res = c.login(username='User1', password='1234567890')
        self.assertTrue(res)
        self.assertEqual(response.json()['count'], 2)

    def test_snippets_details_unauthorized_user(self):
        user = User.objects.get(id=1)
        response = c.get('/snippets/')
        self.assertEqual(response.json()['results'][0]['title'], 'test title1')
        self.assertEqual(response.json()['results'][0]['code'], 'Code1')
        self.assertEqual(response.json()['results'][0]['linenos'], True)
        self.assertEqual(response.json()['results'][0]['language'], 'python')
        self.assertEqual(response.json()['results'][0]['style'], 'friendly')
        self.assertEqual(response.json()['results'][0]['owner'], user.username)


class AddSnippetsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='TestUser1',
                            email='test@tset.test')
        user.set_password('1234567890')
        user.save()

        user = User.objects.create(username='TestUser2',
                                   email='test2@tset.test')
        user.set_password('1234567890')
        user.save()

    def test_add_snippet_unauthorized_user(self):
        r = c.get('/snippets/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = {'code': 'try to create a spippet as unauthorized user'}
        response = c.post('/snippets/', data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
