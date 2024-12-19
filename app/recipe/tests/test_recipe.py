from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APIClient
from core.models import Recipe , Tag , Ingredient
from rest_framework import status
from recipe.serializers import RecipeSerializer , RecipeDetailSerializer

import tempfile
import os

from PIL import Image

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image' , args=[recipe_id])



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

    def test_create_recipe_with_new_tags(self):
        payload={
            'title': ' test recipe',
            'time_minutes' :10,
            'price':Decimal('5.50'),
            'tags':[
                {'name':'delciuos'} , {'name' : 'good'}
            ]
            }
        res=self.client.post(RECIPE_URL , payload , format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe=recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists=recipe.tags.filter(name=tag['name'] , user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        tag=Tag.objects.create(name='indian' , user=self.user)
        payload={
                'title': ' test recipe',
                'time_minutes' :10,
                'price':Decimal('5.50'),
                'tags':[
                    {'name':'delciuos'} , {'name' : 'indian'}
                ]
                }
        res=self.client.post(RECIPE_URL , payload , format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe=recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload['tags']:
            exists=recipe.tags.filter(name=tag['name'] , user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        ''' test update new tag of recipe '''
        recipe=create_recipe(user=self.user)

        payload={'tags':[{'name':'good'}]}
        url=create_recipe_url(recipe.id)
        res=self.client.patch(url , payload , format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        newtag=Tag.objects.get(user=self.user , name='good')
        self.assertIn(newtag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        ''' test assigning existing tag when updating recipe '''
        cur_tag=Tag.objects.create(user=self.user , name='old')
        recipe=create_recipe(user=self.user)
        recipe.tags.add(cur_tag)

        new_tag=Tag.objects.create(user=self.user , name='new')
        url=create_recipe_url(recipe.id)
        payload={'tags':[{'name':'new'}]}
        res=self.client.patch(url , payload , format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_tag, recipe.tags.all())
        self.assertNotIn(cur_tag, recipe.tags.all())

    def test_clear_recipe_tags(self):
        ''' test delete recipr tags '''
        cur_tag=Tag.objects.create(user=self.user , name='old')
        recipe=create_recipe(user=self.user)
        recipe.tags.add(cur_tag)
        payload={'tags':[]}
        url=create_recipe_url(recipe.id)
        res=self.client.patch(url ,payload , format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 0)


    def test_create_recipe_with_new_ingredients(self):
        ''' test create recipe with new ingredients '''
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'ingredients': [ {'name': 'botato' } , {'name': 'tomato' }, ]
        }

        res=self.client.post(RECIPE_URL , payload , format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe=Recipe.objects.filter(user=self.user)

        self.assertEqual(recipe.count(), 1)
        self.assertEqual(recipe[0].ingredients.count(), 2)

        for ingred in payload['ingredients']:

            exist=recipe[0].ingredients.filter(
                user=self.user , name=ingred['name']
                ).exists()

            self.assertTrue(exist)

    def test_create_recipe_with_existing_ingredient(self):
        ''' test create recioe with exstung ingredient '''
        ingred=Ingredient.objects.create(user=self.user , name='ingred1')

        payload={
            'title':'test',
            'price':Decimal('5.50'),
            'time_minutes':10,
            'ingredients':[{'name':'ingred1'} , {'name':'tomato'}]
        }
        res= self.client.post(RECIPE_URL , payload , format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)

        self.assertEqual(len(recipes), 1)
        recipe=recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingred, recipe.ingredients.all())

        for ingred in payload['ingredients']:

            exist=recipe.ingredients.filter(user=self.user , name=ingred['name']).exists()

            self.assertTrue(exist)

    def test_update_recipe_with_new_ingred(self):
        recipe=create_recipe(user=self.user)
        payload = {
            'ingredients': [ {'name': 'botato' } , ]
        }
        url=create_recipe_url(recipe.id)

        res=self.client.patch(url , payload , format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingred=Ingredient.objects.get(user=self.user , name='botato')

        self.assertIn(new_ingred, recipe.ingredients.all())

    def test_update_recipe_with_existing_ingred(self):
        old_ingred=Ingredient.objects.create(user=self.user , name='botato')
        recipe=create_recipe(user=self.user)
        recipe.ingredients.add(old_ingred)

        new_ingred=Ingredient.objects.create(user=self.user , name='tomato')
        payload = {
            'ingredients': [ {'name': 'tomato' } , ]
        }

        url=create_recipe_url(recipe.id)

        res=self.client.patch(url ,payload , format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertNotIn(old_ingred, recipe.ingredients.all())
        self.assertIn(new_ingred, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        old_ingred=Ingredient.objects.create(user=self.user , name='botato')
        recipe=create_recipe(user=self.user)
        recipe.ingredients.add(old_ingred)
        payload = {
            'ingredients': []
        }
        url=create_recipe_url(recipe.id)

        res=self.client.patch(url ,payload , format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

class TestImageUpload(TestCase):
    def setUp(self):
        self.client=APIClient()
        self.user=get_user_model().objects.create_user(
            email='user.example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)
        self.recipe=create_recipe(user=self.user)
    # run after test
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        ''' test upload image '''
        url=image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as img_file:
            img=Image.new('RGB' , (10,10))
            img.save(img_file , format='JPEG')
            img_file.seek(0)
            payload={
                'image' : img_file,
            }
            res=self.client.post(url ,payload , format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_bad_request(self):
        url=image_upload_url(self.recipe.id)
        res=self.client.post(url , {'image':'khkhkh'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_tags(self):
        ''' test filtering recipe by tags '''
        r1=create_recipe(user=self.user , title='test1')
        r2=create_recipe(user=self.user , title='test2')
        t1=Tag.objects.create(user=self.user , name='tag1')
        t2=Tag.objects.create(user=self.user , name='tag2')
        r3=create_recipe(user=self.user , title='test3')
        r1.tags.add(t1)
        r2.tags.add(t2)

        params={'tags':f'{t1.id},{t2.id}'}
        res=self.client.get(RECIPE_URL , params)

        s1=RecipeSerializer(r1)
        s2=RecipeSerializer(r2)
        s3=RecipeSerializer(r3)


        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        ''' test filtering recipe by ingredients '''
        r1=create_recipe(user=self.user , title='test1')
        r2=create_recipe(user=self.user , title='test2')
        ingred1=Ingredient.objects.create(user=self.user , name='ingred1')
        ingred2=Ingredient.objects.create(user=self.user , name='ingred2')
        r3=create_recipe(user=self.user , title='test3')
        r1.ingredients.add(ingred1)
        r2.ingredients.add(ingred2)

        params={
            'ingredients' : f'{ingred1.id},{ingred2.id}',
        }

        s1=RecipeSerializer(r1)
        s2=RecipeSerializer(r2)
        s3=RecipeSerializer(r3)

        res=self.client.get(RECIPE_URL , params)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
