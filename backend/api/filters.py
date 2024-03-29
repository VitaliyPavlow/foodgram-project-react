import re

import django_filters

from django.http import HttpRequest

from recipe.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.CharFilter(
        method="filter_is_in_shopping_cart"
    )
    tags = django_filters.CharFilter(method="filter_is_tags")

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        param = {"favored_by__user": self.request.user}
        if value:
            if int(value) == 1:
                return queryset.filter(**param)
            if int(value) == 0:
                return queryset.exclude(**param)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        param = {"shopping_cart__user": self.request.user}
        if value:
            if int(value) == 1:
                return queryset.filter(**param)
            if int(value) == 0:
                return queryset.exclude(**param)
        return queryset

    def filter_is_tags(self, queryset, name, value):
        url = HttpRequest.get_full_path(self.request)
        matches = re.findall(r"tags=([^&]+)", url)
        tags = [match for match in matches]
        if not tags:
            return queryset.none()
        return queryset.filter(tags__slug__in=tags).distinct()
