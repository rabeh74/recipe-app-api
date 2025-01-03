from rest_framework import serializers
from core.models import Recipe , Tag , Ingredient

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id' , 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id' , 'name']
        read_only_fields = ['id']




class RecipeSerializer(serializers.ModelSerializer ):
    # by deafult nested serializer are read_only
    tags = TagSerializer(many=True , required=False)
    ingredients = IngredientSerializer(many = True , required = False)
    class Meta:
        model=Recipe
        fields=['id' , 'title' , 'price' , 'time_minutes' , 'link' , 'tags' , 'ingredients']
        read_only_fields=['id']

    def _create_or_get_obj(self , tags , recipe):
        auth_user=self.context['request'].user

        for tag in tags:
            tag_obj , created = Tag.objects.\
                get_or_create(user=auth_user , **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingred(self , ingredients , recipe):
        auth_user=self.context['request'].user

        for ingred in ingredients:
            ingred_obj , created = Ingredient.objects.\
                get_or_create(user=auth_user , **ingred)
            recipe.ingredients.add(ingred_obj)

    def create(self , validated_data):
        tags = validated_data.pop('tags' , [])
        ingredients = validated_data.pop('ingredients' , [])
        recipe = Recipe.objects.create(**validated_data)

        self._create_or_get_obj(tags, recipe)
        self._get_or_create_ingred(ingredients , recipe)

        return recipe

    def update(self, instance, validated_data):
        tags=validated_data.pop('tags' , None)
        ingreds=validated_data.pop('ingredients' , None)
        if tags is not None :
            instance.tags.clear()
            self._create_or_get_obj(tags, instance)
        if ingreds is not None:
            instance.ingredients.clear()
            self._get_or_create_ingred(ingreds, instance)

        for k , v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields

# to seperate types as image different from other basic types
class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Recipe
        fields=['id' , 'image']
        read_only_fields=['id']
        extra_kwargs={
            'image':{'required':True}
        }
