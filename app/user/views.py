from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


from user.serializers import (UserSerializer,AuthTokenSerializer)

class UserCreateView(generics.CreateAPIView):
    """ Crete a new user in system """
    serializer_class=UserSerializer

class AuthTokenView(ObtainAuthToken):
    '''create token for user '''
    serializer_class=AuthTokenSerializer # to validate auth based on email not in name
    renderer_classes=api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    ''' manage auth user , methid get put patch  '''
    serializer_class=UserSerializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get_object(self):
        ''' retireve and return authenticared user '''
        return self.request.user