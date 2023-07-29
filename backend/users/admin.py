from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Subscription, User


class EmailFilter(admin.SimpleListFilter):
    title = "Email"
    parameter_name = "email"

    def lookups(self, request, model_admin):
        return [
            (email, email)
            for email in User.objects.values_list(
                "email", flat=True
            ).distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(email=value)
        return queryset


class UsernameFilter(admin.SimpleListFilter):
    title = "Username"
    parameter_name = "username"

    def lookups(self, request, model_admin):
        return [
            (username, username)
            for username in User.objects.values_list(
                "username", flat=True
            ).distinct()
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(username=value)
        return queryset


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "id", "email", "first_name", "last_name")
    list_filter = (EmailFilter, UsernameFilter)
    fieldsets = (
        (
            "Информация о пользователе",
            {
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                )
            },
        ),
        (
            "Информация об активности",
            {"fields": ("last_login", "date_joined")},
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "author")


admin.site.unregister(Group)
