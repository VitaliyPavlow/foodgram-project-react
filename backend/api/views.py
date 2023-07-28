import datetime

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, generics, serializers, status, viewsets
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipe.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Subscription, User

from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthor
from .serializers import (
    IngredientSerializer, RecipeSerializer, RecipeSubscriptionSerializer,
    SubscriptionsSerializer, TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ["get"]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]

    def get_queryset(self):
        return Recipe.objects.select_related("author").prefetch_related(
            "tags", "ingredients"
        )

    def perform_create(self, serializer):
        tag_pk = self.request.data.pop("tags", [])
        ingredients_list = self.request.data.pop("ingredients", [])

        if not tag_pk:
            raise serializers.ValidationError({"tags": ["Обязательное поле."]})
        if not ingredients_list:
            raise serializers.ValidationError(
                {"ingredients": ["Обязательное поле."]}
            )

        tags = Tag.objects.filter(pk__in=tag_pk)
        recipe = serializer.save()
        for ingredient in ingredients_list:
            amount = ingredient["amount"]
            ingredient_obj = get_object_or_404(Ingredient, pk=ingredient["id"])
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient_obj, amount=amount
            )
        recipe.tags.set(tags)

    def partial_update(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs["pk"])
        if "tags" in request.data.keys():
            if not request.data["tags"]:
                raise serializers.ValidationError(
                    {"tags": ["Обязательное поле."]}
                )
            tag_pk = self.request.data.pop("tags", [])
            tags = Tag.objects.filter(pk__in=tag_pk)
            recipe.tags.set(tags)

        ingredients_list = self.request.data.pop("ingredients", [])
        for ingredient in ingredients_list:
            amount = ingredient["amount"]
            if amount < 1:
                raise serializers.ValidationError(
                    {
                        "amount": [
                            "Убедитесь, что это значение больше либо равно 1."
                        ]
                    }
                )
            ingredient_obj = get_object_or_404(Ingredient, pk=ingredient["id"])

            recipe_ingredient, create = RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                defaults={"amount": amount},
            )

            if not create:
                recipe_ingredient.amount = amount
                recipe_ingredient.save()

        return super().partial_update(request, *args, **kwargs)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ["get"]
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class SubscribesListView(generics.ListAPIView):
    serializer_class = SubscriptionsSerializer
    pagination_class = PageLimitPagination
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        return (
            User.objects.filter(following__user=self.request.user)
            .prefetch_related("following", "recipes")
            .annotate(recipes_count=Count("recipes"))
        )


class SubscribeUnsubscribeView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = SubscriptionsSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs["id"])
        user = self.request.user
        if author == user:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription, create = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if not create:
            return Response(
                {"errors": "Подписка уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        author = User.objects.annotate(recipes_count=Count("recipes")).get(
            id=author.id
        )
        serializer = self.get_serializer(
            author, context={"request": self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        deleted = Subscription.objects.filter(
            author__id=kwargs["id"], user=self.request.user
        ).delete()
        if deleted[0] == 0:
            return Response(
                {"errors": "Вы не подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = RecipeSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["id"])
        user = self.request.user
        favorite, create = Favorite.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not create:
            return Response(
                {"errors": "Рецепт уже в избранном."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            recipe, context={"request": self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        deleted = Favorite.objects.filter(
            user=self.request.user, recipe__id=kwargs["id"]
        ).delete()
        if deleted[0] == 0:
            return Response(
                {"errors": "Вы ещё не добавили этот рецепт в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_ingredients_list(self):
        ingredients_list = []
        user = self.request.user
        unique_ingredients = (
            Ingredient.objects.filter(
                recipe_ingredient__recipe__shopping_cart__user=user
            )
            .distinct()
            .prefetch_related("recipe_ingredient")
        )
        for ingredient in unique_ingredients:
            amount = ingredient.recipe_ingredient.all().aggregate(
                Sum("amount")
            )
            string = (
                f"\u2611   {ingredient.name} ({ingredient.measurement_unit}) "
                f"- {int(amount['amount__sum'])}"
            )
            ingredients_list.append(string)
        return ingredients_list

    def get(self, request, *args, **kwargs):
        date = datetime.datetime.now().strftime("%d-%m-%y")
        response = HttpResponse(content_type="application/pdf; charset=utf-8")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="shopping_cart_{date}.pdf"'
        pdfmetrics.registerFont(TTFont("Verdana", "fonts/Verdana.ttf"))
        page = canvas.Canvas(response)

        page.setFont("Verdana", 20)
        title = f"Ваш список покупок на сегодня {date}"
        page.drawString(60, 750, title)
        page.line(60, 730, 500, 730)

        page.setFont("Verdana", 12)
        data = self.get_ingredients_list()
        y = 670
        for string in data:
            page.drawString(60, y, string)
            y -= 30
        page.showPage()
        page.save()
        return response


class ShoppingCartCreateDeleteView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = RecipeSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["id"])
        user = self.request.user
        shopping_cart, create = ShoppingCart.objects.get_or_create(
            user=user, recipe=recipe
        )
        if not create:
            return Response(
                {"errors": "Рецепт уже в списке покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            recipe, context={"request": self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        deleted = ShoppingCart.objects.filter(
            user=self.request.user, recipe__id=kwargs["id"]
        ).delete()
        if deleted[0] == 0:
            return Response(
                {"errors": "Вы ещё не добавили этот рецепт в список покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersListView(UserViewSet):
    pagination_class = PageLimitPagination
