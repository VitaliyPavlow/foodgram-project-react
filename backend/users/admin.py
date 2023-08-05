from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Subscription, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "id", "email", "first_name", "last_name")
    search_fields = ["username", "email"]
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
