import re

from foodgram_backend import settings

from django.core.exceptions import ValidationError


def validate_username(name):
    if name in settings.RESERVED_USERNAMES:
        raise ValidationError(f"Имя пользователя не может быть {name}.")


def validate_username_bad_sign(name):
    invalid_chars = re.findall(r"[^a-zA-Z0-9.@+-]+", name)
    if invalid_chars:
        simbols = " ".join(set(invalid_chars))
        raise ValidationError(
            f"Имя пользователя содержит недопустимые символы: {simbols}"
        )
