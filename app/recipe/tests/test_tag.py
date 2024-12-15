from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag,Recipe

from recipe.serializers import TagSerializer

def tag_url(tag_id):
    return reverse('recipe:tag-detail' , args=[tag_id])

def create_user(email='test6@example.com' , password='testpass123'):
    return get_user_model().objects.create_user(email=email , password=password)

TAG_URL=reverse('recipe:tag-list')

class PublicTagTest(TestCase):
    ''' test un authorized api request '''
    def setUp(self):
        self.client=APIClient()

    def test_tag_for_unauth(self):

        res=self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagTest(TestCase):
    ''' test authorized api requests '''
    def setUp(self):
        self.user=create_user()
        self.client=APIClient()

        self.client.force_authenticate(self.user)

    def test_retriev_tag(self):
        ''' test list of tags to authenticated user '''

        Tag.objects.create(user=self.user , name='test1')
        Tag.objects.create(user=self.user , name='test2')

        res=self.client.get(TAG_URL)
        tags=Tag.objects.all().order_by('-name')
        serializser=TagSerializer(tags , many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializser.data)

    def test_retireve_tag_limitedto_user(self):
        ''' test list of tags limited to authenticated user '''
        user=create_user(email='test3@example.com')
        Tag.objects.create(user=user , name='test1')
        tag=Tag.objects.create(user=self.user , name='test2')

        res=self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tage(self):
        ''' test for update tag '''
        tag=Tag.objects.create(user=self.user , name='test1')
        payload={
            'name':'test6'
        }
        url=tag_url(tag.id)
        res=self.client.patch(url , payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        ''' test for delete tag '''
        tag = Tag.objects.create(user=self.user , name='test1')
        url=tag_url(tag.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

