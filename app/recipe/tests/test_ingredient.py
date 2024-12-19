from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Ingredient,Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL=reverse('recipe:ingredient-list')

def create_ingred_url(ingred_id):
    return reverse('recipe:ingredient-detail' , args=[ingred_id])

def create_user(email='test3@example.com' , password='testpass123'):
    return get_user_model().objects.create_user\
        (email=email , password=password)

class PublicTestIngredientApi(TestCase):
    ''' test ingredient public request '''
    def setUp(self):
        self.client=APIClient()

    def test_auth_requied(self):
        ''' auth is requied for retiving ingredients '''
        res=self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientTestApi(TestCase):

    ''' test auth api request '''
    def setUp(self):
        self.user=create_user()
        self.client=APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_list_ingredent(self):
        ''' test retrive list of ingredients '''
        Ingredient.objects.create(user=self.user , name='test1')
        Ingredient.objects.create(user=self.user , name='test2')

        res=self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingreds=Ingredient.objects.all().order_by('-name')
        serializer=IngredientSerializer(ingreds , many=True)

        self.assertEqual(serializer.data, res.data)

    def test_ingred_limited_to_user(self):
        ''' test ingred limited to auth user '''
        user=create_user(email='tes@example.com')
        Ingredient.objects.create(user=user , name='test1')
        Ingredient.objects.create(user=self.user , name='test2')

        res=self.client.get(INGREDIENTS_URL)
        ingred=Ingredient.objects.filter(user=self.user)
        serializer=IngredientSerializer(ingred , many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingred[0].name)

    def test_update_ingredient(self):
        ingred = Ingredient.objects.create(user=self.user , name='test2')
        payload={
            'name':'tomatto'
        }
        url=create_ingred_url(ingred.id)
        res=self.client.patch(url , payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingred.refresh_from_db()

        self.assertEqual(ingred.name, payload['name'])

    def test_delete_ingredient(self):
        ''' tset delete ingredient '''
        ingred=Ingredient.objects.create(user=self.user , name='test')

        url=create_ingred_url(ingred.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Ingredient.objects.filter(id=ingred.id).exists())

    def test_ingredients_assigned_to_recipe(self):
        in1=Ingredient.objects.create(user=self.user , name='ing1')
        in2=Ingredient.objects.create(user=self.user , name='ing2')

        recipe=Recipe.objects.create(
            user=self.user,
            price=5.0,
            time_minutes=10,
            title='test ingred'
        )
        recipe.ingredients.add(in1)
        s1=IngredientSerializer(in1)
        s2=IngredientSerializer(in2)
        res=self.client.get(INGREDIENTS_URL , {'assigned_only':1})

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_ingredients_assigned_unique(self):
        in1=Ingredient.objects.create(user=self.user , name='ing1')
        Ingredient.objects.create(user=self.user , name='ing2')

        recipe1=Recipe.objects.create(
            user=self.user,
            price=5.0,
            time_minutes=10,
            title='test ingred'
        )
        recipe2=Recipe.objects.create(
            user=self.user,
            price=5.0,
            time_minutes=10,
            title='test ingred2'
        )

        recipe1.ingredients.add(in1)
        recipe2.ingredients.add(in1)
        res=self.client.get(INGREDIENTS_URL , {'assigned_only':1})
        self.assertEqual(len(res.data), 1)
