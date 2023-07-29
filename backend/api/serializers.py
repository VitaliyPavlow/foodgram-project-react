import base64

from djoser.serializers import (
    TokenCreateSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from rest_framework import serializers

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipe.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User
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

    def get_is_subscribed(self, obj):
        if not self.context["request"].user.is_authenticated:
            return False
        return (
            self.context["request"].user.follower.filter(author=obj).exists()
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
        ingredient = get_object_or_404(Ingredient, pk=pk)
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


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredient", many=True
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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

    def save(self, **kwargs):
        self.validated_data["author"] = self.context["request"].user
        return super().save(**kwargs)

    def create(self, validated_data):
        validated_data.pop("recipe_ingredient")
        return super().create(validated_data)

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.favored_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.shopping_cart.filter(user=user).exists()


class RecipeSubscriptionSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(serializers.ModelSerializer):
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, obj):
        return obj.following.all().exists()

    def get_recipes(self, obj):
        recipes_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes_queryset = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            recipes_queryset = recipes_queryset[:recipes_limit]
        return RecipeSubscriptionSerializer(recipes_queryset, many=True).data
