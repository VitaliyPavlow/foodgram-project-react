from rest_framework.authtoken.models import TokenProxy

from django import forms
from django.contrib import admin
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


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "display_image", "text", "cooking_time")
    inlines = [RecipeIngredientInline]

    # def display_image(self, obj):
    #     return obj.image.url if obj.image else ''

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100%; max-height: 80px;" />',
                obj.image.url,
            )
        else:
            return ""

    display_image.short_description = "Image"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")


class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

    def clean_color(self):
        value = self.cleaned_data.get("color")
        hex_color_validator(value)
        return value


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    form = TagAdminForm


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.unregister(TokenProxy)
