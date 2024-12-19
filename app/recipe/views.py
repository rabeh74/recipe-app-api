from rest_framework import (viewsets , mixins , status)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from recipe.serializers import (RecipeSerializer,RecipeDetailSerializer,
TagSerializer , IngredientSerializer , RecipeImageSerializer)
from core.models import Recipe,Tag,Ingredient

from rest_framework.response import Response

from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='comma seperaeted list to filter recipe by tags'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='comma seperaeted list to filter recipe by ingredients'
            ),

        ]
    )
)

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class=RecipeDetailSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    queryset=Recipe.objects.all()

    def _params_to_ints(self , qs):
        return [int(params_id) for params_id in qs.split(',') ]

    def get_queryset(self):
        tags=self.request.query_params.get("tags")
        ingredients=self.request.query_params.get('ingredients')

        queryset=self.queryset

        if tags:

            tags_ids=self._params_to_ints(tags)
            queryset=queryset.filter(tags__id__in=tags_ids)


        if ingredients:
            ingred_ids=self._params_to_ints(ingredients)
            queryset=queryset.filter(ingredients__id__in = ingred_ids)
        return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        if self.action=='list':
            return RecipeSerializer

        elif self.action=='upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self , serializer ):
        serializer.save(user = self.request.user)
    # detail means specefic id of recipe , detail view

    @action(methods=['POST'] , detail=True , url_path='upload-image')
    def upload_image(self , request , pk=None):
        recipe=self.get_object()
        seriapizer=self.get_serializer(recipe , data=request.data)

        if seriapizer.is_valid():
            seriapizer.save()
            return Response(seriapizer.data , status=status.HTTP_200_OK)

        return Response(seriapizer.errors , status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT ,
                enum=[0,1],
                description='filter by items assigned to recipe '
            ),

        ]
    )
)

class BaserecipeItem(viewsets.ModelViewSet):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        ''' filter auery according to auth user '''
        queryset=self.queryset
        assinged_only=bool(int(self.request.query_params.get('assigned_only' , 0)))
        if assinged_only:
            queryset=queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name').distinct()
    def perform_create(self , serializer ):
        serializer.save(user = self.request.user)


class TagViewSet(BaserecipeItem):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaserecipeItem):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()





