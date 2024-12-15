from unittest.mock import patch

from django.contrib.auth import get_user_model
from core import models
from django.test import TestCase
from decimal import Decimal
def create_user(email='test1@example.com' , password='testpass123'):
    user=get_user_model().objects.create_user(email=email , password=password)
    return user

class ModelTests(TestCase):
    def test_create_user_with_email_password(self):
        email='test@example.com'
        password='pass12345'
        user=create_user(email , password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalize(self):
        smaple_emails=[
            ['TEST@EXaMPLE.COM' , 'TEST@example.com'],
            ['TEST1@example.COM' , 'TEST1@example.com'],
            ['test2@example.COM' , 'test2@example.com'],
            ['Test3@EXample.COM' , 'Test3@example.com'],

        ]
        for email , expected_email in smaple_emails:
            user=get_user_model().objects.create_user(email=email , password='test1234')
            self.assertEqual(user.email, expected_email)

    def test_user_without_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('' , 'teat123')

    def test_create_super_user(self):
        user=get_user_model().objects.create_superuser(email='test4@example.com' ,\
             password='test123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_recipe(self):
        ''' test for creating recipe '''
        user=get_user_model().objects.create_user\
            (email='test@example.com' ,
            password='testpass123' ,)

        recipe=models.Recipe.objects.create(
            user=user,
            title= 'simple recipe test',
            time_minutes=5,
            price=Decimal('15.5'),
            description='sample recipe description '
        )
        self.assertEqual(str(recipe), recipe.title)
