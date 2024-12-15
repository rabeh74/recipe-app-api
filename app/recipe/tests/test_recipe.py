from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from core.models import Recipe
from rest_framework import status
from recipe.serializers import RecipeSerializer , RecipeDetailSerializer

import tempfile
import os

from PIL import Image

# def image_upload_url(recipe_id):
#     return reverse('recipe:recipe-upload-image' , args=[recipe_id])



RECIPE_URL=reverse('recipe:recipe-list')

def create_recipe_url(recipe_id):
    ''' create and return url for recipe detail '''
    return reverse('recipe:recipe-detail' , args=[recipe_id])

def create_recipe(user , **kwargs):
    defaults={
        'title':'samp;e test',
        'user':user,
        'price':10,
        'time_minutes':Decimal('5.50'),
        'description':'test descriprion'

    }
    defaults.update(**kwargs)
    recipe=Recipe.objects.create(**defaults)
    return recipe

class PublicTestRecipeApi(TestCase):
    ''' test list recipe for unauthoied user'''
    def setUp(self):
        self.client=APIClient()

    def test_auth_required(self):
        ''' test auth is required for api requests'''
        res=self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTest(TestCase):
    ''' test auth api requests '''
    def setUp(self):
        self.client=APIClient()
        self.user=get_user_model().objects.create_user\
            (email='test@example.com' ,
            password='testpass123',
            )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        ''' test retrieve list of recipe '''
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res=self.client.get(RECIPE_URL)
        recipes=Recipe.objects.all().order_by('-id')
        serilizers=RecipeSerializer(recipes , many=True)

        self.assertEqual(serilizers.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_for_auth_user(self):
        ''' retrive list of recipe that is limited to auth user '''
        user=get_user_model().objects.create_user\
            (email='test2@example.com' ,
            password='testpass123',
            )
        create_recipe(user=user)
        create_recipe(user=self.user)
        res=self.client.get(RECIPE_URL)
        recipes=Recipe.objects.filter(user=self.user)
        serializers = RecipeSerializer(recipes , many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializers.data, res.data)

    def test_recipe_detail(self):
        ''' test get recipe detail '''

        recipe=create_recipe(user=self.user)
        url=create_recipe_url(recipe.id)
        res=self.client.get(url)
        serializer=RecipeDetailSerializer(recipe)

        self.assertEqual(serializer.data, res.data)

    def test_create_recipe(self):
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        res=self.client.post(RECIPE_URL , payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe=Recipe.objects.get(id=res.data['id'])

        for k , v in payload.items():
            self.assertEqual(getattr(recipe , k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        ''' test partial update '''
        recipe=Recipe.objects.create(
            title='simple',
            user=self.user,
            price=Decimal(5.60),
            time_minutes=5
        )
        url=create_recipe_url(recipe.id)
        res=self.client.patch(url , {'title':'updated'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'updated')

    def test_full_update(self):
        pass

    def test_update_user_return_nothing(self):
        ''' tset try to change the recipe usr will not affect '''
        user=get_user_model().objects.create_user\
            (email='test3@example.com' , password='test123')

        recipe=create_recipe(user=self.user)
        payload={
            'user':user
        }
        url=create_recipe_url(recipe.id)
        res=self.client.patch(url)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        ''' test delete recipe '''

        recipe=create_recipe(user=self.user)
        url=create_recipe_url(recipe.id)
        res=self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe(self):
        user=get_user_model().objects.create_user\
            (email='test3@example.com' , password='test123')
        recipe=create_recipe(user=user)
        url=create_recipe_url(recipe.id)

        res=self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
