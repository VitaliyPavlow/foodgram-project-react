import datetime

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
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

from .pagination import SubscribePagination
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeSubscriptionSerializer,
    SubscriptionsSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ["get"]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ["get"]
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class SubscribesListView(generics.ListAPIView):
    serializer_class = SubscriptionsSerializer
    pagination_class = SubscribePagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscribeUnsubscribeView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = SubscriptionsSerializer

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
        serializer = self.get_serializer(
            author, context={"request": self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs["id"])
        user = self.request.user
        try:
            subscription = Subscription.objects.get(user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"errors": "Вы не подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FavoriteView(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = RecipeSubscriptionSerializer

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
        recipe = get_object_or_404(Recipe, id=kwargs["id"])
        user = self.request.user
        try:
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"errors": "Вы ещё не добавили этот рецепт в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ShoppingCartView(APIView):
    def get_ingredients_list(self):
        ingredients_unique_pk = set()
        ingredients_list = []
        recipes_list = Recipe.objects.filter(
            shoppinng_cart__user=self.request.user
        )
        for recipe in recipes_list:
            {
                ingredients_unique_pk.add(ingredient.ingredient.pk)
                for ingredient in recipe.recipe_ingredient.all()
            }
        for pk in ingredients_unique_pk:
            ingredient = Ingredient.objects.get(pk=pk)
            amount = RecipeIngredient.objects.filter(
                ingredient=pk, recipe__in=recipes_list
            ).aggregate(Sum("amount"))
            string = f"\u2611 {ingredient.name} ({ingredient.measurement_unit}) - {int(amount['amount__sum'])}"
            ingredients_list.append(string)
        return ingredients_list

    def get(self, request, *args, **kwargs):
        date = datetime.datetime.now().strftime("%d-%m-%y")
        response = HttpResponse(content_type="application/pdf; charset=utf-8")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="shopping_cart_{date}.pdf"'
        pdfmetrics.registerFont(TTFont("Verdana", "fonts/Verdana.ttf"))
        p = canvas.Canvas(response)

        p.setFont("Verdana", 20)
        title = f"Ваш список покупок на сегодня {date}"
        p.drawString(60, 750, title)
        p.line(60, 730, 500, 730)

        p.setFont("Verdana", 12)
        data = self.get_ingredients_list()
        y = 670
        for string in data:
            p.drawString(60, y, string)
            y -= 30
        p.showPage()
        p.save()
        return response


class ShoppingCartCreateDeleteView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = RecipeSubscriptionSerializer

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
        recipe = get_object_or_404(Recipe, id=kwargs["id"])
        user = self.request.user
        try:
            shopping_cart = ShoppingCart.objects.get(user=user, recipe=recipe)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"errors": "Вы ещё не добавили этот рецепт в список покупок."},
                status=status.HTTP_400_BAD_REQUEST,
            )
