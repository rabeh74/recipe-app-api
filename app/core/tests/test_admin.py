from django.contrib.auth import get_user_model
from django.test import TestCase,Client
from django.urls import reverse

class AdminUserTest(TestCase):
    def setUp(self):
        self.client=Client()

        self.admin=get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin)

        self.user=get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='test user'
        )

    def test_user_lists(self):
        url=reverse('admin:core_user_changelist') #from docs
        res=self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url=reverse('admin:core_user_change' , args=[self.user.id]) #from docs
        res=self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        url=reverse('admin:core_user_add') #from docs
        res=self.client.get(url)
        self.assertEqual(res.status_code, 200)