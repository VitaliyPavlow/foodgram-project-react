from rest_framework import routers

from django.urls import include, path

from .views import (
    FavoriteView,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartCreateDeleteView,
    ShoppingCartView,
    SubscribesListView,
    SubscribeUnsubscribeView,
    TagViewSet,
    UsersListView,
)


router = routers.DefaultRouter()
router.register(r"tags", TagViewSet)
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet)


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("users/", UsersListView.as_view({"get": "list", "post": "create"})),
    path("users/subscriptions/", SubscribesListView.as_view()),
    path("users/<int:id>/subscribe/", SubscribeUnsubscribeView.as_view()),
    path("recipes/<int:id>/favorite/", FavoriteView.as_view()),
    path("recipes/download_shopping_cart/", ShoppingCartView.as_view()),
    path(
        "recipes/<int:id>/shopping_cart/",
        ShoppingCartCreateDeleteView.as_view(),
    ),
    path("", include(router.urls)),
    path("", include("djoser.urls")),
]
