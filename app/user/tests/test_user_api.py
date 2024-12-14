from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core import models
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL= reverse('user:create') # user app , create is the name of endpoint in app
TOKEN_URL=reverse('user:token')
ME_URL=reverse('user:me')

def create_user(**kwargs):
    user=get_user_model().objects.create_user(**kwargs)

    return user
class PublicUserAPITest(TestCase):
    """ Test public User API """
    def setUp(self):
        self.client=APIClient()

    def test_create_user_success(self):
        """test creating a user is successful"""
        payload={
            'email':'testuser@gmail.com',
            'name':'test user',
            'password':'testpass123'
        }
        res=self.client.post(CREATE_USER_URL , payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user=get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_create_user_with_email_exitsts_erro(self):
        """
        Test error returned if create user with email already exists
        """
        payload={
            'email':'testuser@gmail.com',
            'name':'test user',
            'password':'testpass123'
        }
        create_user(**payload)
        res=self.client.post(CREATE_USER_URL , payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_with_small_password_error(self):
        """
        Test error returned if create user with password less than 5 chars
        """
        payload={
            'email':'testuser@gmail.com',
            'name':'test user',
            'password':'123'
        }
        res=self.client.post(CREATE_USER_URL , payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user=get_user_model().objects.filter(email=payload['email']).exists()

        self.assertFalse(user)

    def test_create_token_for_user(self):
        '''test generate tkens for valid credentionals'''
        user_detatils={
            'name':'test user',
            'password': 'testpass123',
            'email':'test@example.com',
        }
        create_user( **user_detatils )

        payload={
            'email':user_detatils['email'],
            'password':user_detatils['password']
        }

        res=self.client.post(TOKEN_URL , payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_bad_credentials(self):
        ''' test returns error if credentials are invalid'''

        create_user(email='test@example.com' , password='testpass123')
        payload={
            'email':'t@example.com',
            'password':'passtest123',
        }
        res=self.client.post(TOKEN_URL , payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_blank_password(self):
        ''' test returns error if password is blank'''

        create_user(email='test@example.com' , password='testpass123')
        payload={
            'email':'test@example.com',
            'password':'',
        }
        res=self.client.post(TOKEN_URL , payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_for_unauthorized_user(self):
        res=self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTest(TestCase):
    '''test for private api '''
    def setUp(self):
        self.user=create_user(email='test@example.com' , \
            password ='testpass123' , name='test name')
        self.client=APIClient()

        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        '''test retrive profile for logged in user'''
        res=self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name':self.user.name,
            'email':self.user.email})

    def test_post_me_not_allowd(self):
        res=self.client.post(ME_URL , {})

        self.assertEqual(res.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        payload={'name':'updated name' , 'password' : 'newpass123'}

        res=self.client.patch(ME_URL , payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)