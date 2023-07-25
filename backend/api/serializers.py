import base64

from djoser.serializers import (
    TokenCreateSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from recipe.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from users.validators import validate_username, validate_username_bad_sign


MAX_CHAR_LENGTH = 150


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        if type(self.context["request"].user) == AnonymousUser:
            return False
        return (
            self.context["request"].user.follower.filter(author=obj).exists()
        )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField()
    username = serializers.CharField(
        required=True,
        max_length=MAX_CHAR_LENGTH,
        validators=[validate_username, validate_username_bad_sign],
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password")


class CustomTokenCreateSerializer(TokenCreateSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "ingredient", "amount")

    def to_internal_value(self, data):
        pk = data["id"]
        amount = data["amount"]
        ingredient = Ingredient.objects.get(pk=pk)
        data_plus = {
            "ingredient": {
                "id": ingredient.pk,
                "name": ingredient.name,
                "measurement_unit": ingredient.measurement_unit,
            },
            "amount": amount,
        }
        return super().to_internal_value(data_plus)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient_data = representation.pop("ingredient")
        representation.update(ingredient_data)
        amount = representation.pop("amount")
        representation["amount"] = float(amount)
        return representation

    # def create(self, validated_data):
    #     amount = validated_data.get("amount")
    #     if amount < 1:
    #         raise serializers.ValidationError({"amount": ["Убедитесь, что это значение больше либо равно 1."]})
    #     return super().create(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredient", many=True
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        validated_data.pop("recipe_ingredient")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # validated_data.pop("recipe_ingredient")
        return super().update(instance, validated_data)

    def save(self, **kwargs):
        self.validated_data["author"] = self.context["request"].user
        return super().save(**kwargs)

    # def to_internal_value(self, data):
    #     tags_data = data.pop('tags', [])
    #     validated_data = super().to_internal_value(data)
    #     tags_obj = Tag.objects.filter(pk__in=tags_data)
    #     validated_data['tags'] = tags_obj
    #     return validated_data

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if type(user) == AnonymousUser:
            return False
        return obj.favored_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if type(user) == AnonymousUser:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeSubscriptionSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        return obj.following.all().exists()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes_queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            recipes_queryset = recipes_queryset[:recipes_limit]
        return RecipeSubscriptionSerializer(recipes_queryset, many=True).data

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
