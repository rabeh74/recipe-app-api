from django.urls import path
from user.views import *
app_name='user'


urlpatterns=[

path('create/' ,UserCreateView.as_view() , name='create'),
path('token/' ,AuthTokenView.as_view() , name='token'),
path('me/' ,ManageUserView.as_view() , name='me'),


]