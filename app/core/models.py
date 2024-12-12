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

