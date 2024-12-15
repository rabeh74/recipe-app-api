from django.urls import reverse,include,path
from recipe.views import RecipeViewSet , TagViewSet
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
app_name='recipe'

urlpatterns=[
    path('' , include(router.urls)),
]