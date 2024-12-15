from rest_framework import serializers
from core.models import Recipe , Tag

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id' , 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer ):
    # by deafult nested serializer are read_only
    tags = TagSerializer(many=True , required=False)
    class Meta:
        model=Recipe
        fields=['id' , 'title' , 'price' , 'time_minutes' , 'link' , 'tags']
        read_only_fields=['id']

    def _create_or_get_obj(self , tags , recipe):
        auth_user=self.context['request'].user

        for tag in tags:
            tag_obj , created = Tag.objects.\
                get_or_create(user=auth_user , **tag)
            recipe.tags.add(tag_obj)

    def create(self , validated_data):
        tags = validated_data.pop('tags' , [])
        recipe = Recipe.objects.create(**validated_data)

        self._create_or_get_obj(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags=validated_data.pop('tags' , None)
        ingreds=validated_data.pop('ingredients' , None)
        if tags is not None :
            instance.tags.clear()
            self._create_or_get_obj(tags, instance)

        for k , v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields

