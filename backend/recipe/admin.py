from typing import Any

from rest_framework.authtoken.models import TokenProxy

from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .validators import hex_color_validator


class RecipeAuthorFilter(admin.SimpleListFilter):
    title = "Автор"
    parameter_name = "author"

    def lookups(self, request, model_admin):
        return [
            (author, author)
            for author in Recipe.objects.order_by()
            .values_list("author__username", flat=True)
            .distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(author__username=value)
        return queryset


class RecipeNameFilter(admin.SimpleListFilter):
    title = "Рецепт"
    parameter_name = "name"

    def lookups(self, request, model_admin):
        return [
            (name, name)
            for name in Recipe.objects.order_by()
            .values_list("name", flat=True)
            .distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(name=value)
        return queryset


class RecipeTagFilter(admin.SimpleListFilter):
    title = "Тэги"
    parameter_name = "tags"

    def lookups(self, request, model_admin):
        return [
            (tags, tags)
            for tags in Recipe.objects.order_by()
            .values_list("tags__name", flat=True)
            .distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(tags__name=value)
        return queryset


class IngredientFilter(admin.SimpleListFilter):
    title = "Ингредиенты"
    parameter_name = "name"

    def lookups(self, request, model_admin):
        return [
            (name, name)
            for name in Ingredient.objects.order_by()
            .values_list("name", flat=True)
            .distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(name=value)
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "display_image",
        "text",
        "cooking_time",
        "pub_date",
        "favorite_count",
    )
    inlines = [RecipeIngredientInline]
    list_filter = (RecipeAuthorFilter, RecipeNameFilter, RecipeTagFilter)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("ingredients", "tags")
        )

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100%; max-height: 80px;" />',
                obj.image.url,
            )

    display_image.short_description = "Image"

    def favorite_count(self, obj):
        return obj.favored_by.count()

    favorite_count.short_description = "Добавлено в избранное"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ["name"]
    list_filter = [
        IngredientFilter,
    ]


class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name", "color")

    def clean_color(self):
        value = self.cleaned_data.get("color")
        hex_color_validator(value)
        return value


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    form = TagAdminForm


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("ingredient", "recipe")
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "recipe")


admin.site.unregister(TokenProxy)
