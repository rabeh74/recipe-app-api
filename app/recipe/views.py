from rest_framework import (viewsets , mixins , status)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import (RecipeSerializer , RecipeDetailSerializer ,
                             TagSerializer , IngredientSerializer)
from core.models import Recipe , Tag , Ingredient

from rest_framework.response import Response

from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

class BaserecipeItem(viewsets.ModelViewSet):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return self.queryset.filter(user = self.request.user).order_by('-name')

    def perform_create(self , serializer ):
        serializer.save(user = self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class=RecipeDetailSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    queryset=Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user = self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action=='list':
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self , serializer ):
        serializer.save(user = self.request.user)


class TagViewSet(BaserecipeItem):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaserecipeItem):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()





