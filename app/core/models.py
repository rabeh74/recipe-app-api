from django.db import models
from django.conf import settings
import uuid
import os
# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser ,
    BaseUserManager ,
    PermissionsMixin,
)

def recipe_image_file_path(instance , filename):
    ext=os.path.splitext(filename)[1]
    filename=f'{uuid.uuid4()}{ext}'
    return os.path.join( 'uploads','recipe' , filename)

class UserManager(BaseUserManager):
    def create_user(self , email , password=None , **kwargs):
        if not email:
            raise ValueError('email is not validate ')

        user=self.model(email=self.normalize_email(email) , **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self , email , password):
        user=self.create_user(email , password)
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser , PermissionsMixin):
    email = models.EmailField( max_length=255 , unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects=UserManager()
    USERNAME_FIELD= 'email'

class Recipe(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    price=models.DecimalField( max_digits=5, decimal_places=2)
    time_minutes=models.IntegerField()
    link=models.CharField(blank=True, max_length=255)
    # tags=models.ManyToManyField('Tag')
    # ingredients=models.ManyToManyField('Ingredient')
    image=models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title