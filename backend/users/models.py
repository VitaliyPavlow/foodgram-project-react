from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username, validate_username_bad_sign


MAX_LENGHT_USER_EMAIL = 254
MAX_LENGHT_USER_FIRST = 150
MAX_LENGHT_USER_LAST = 150
MAX_LENGHT_USER_PASSWORD = 150


class User(AbstractUser):
    email = models.EmailField(
        "Email",
        unique=True,
        max_length=MAX_LENGHT_USER_EMAIL,
    )
    first_name = models.CharField("Имя", max_length=MAX_LENGHT_USER_FIRST)
    last_name = models.CharField("Фамилия", max_length=MAX_LENGHT_USER_LAST)
    password = models.CharField("Пароль", max_length=MAX_LENGHT_USER_PASSWORD)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    def __str__(self):
        return f"{self.user} подписан на {self.author}."

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            )
        ]
