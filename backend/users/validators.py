import re

from django.core.exceptions import ValidationError

from foodgram_backend.settings import RESERVED_USERNAMES


def validate_username(name):
    if name in RESERVED_USERNAMES:
        raise ValidationError(
            {"username": f"Имя пользователя не может быть {name}."}
        )


def validate_username_bad_sign(name):
    invalid_chars = re.findall(r"[^\w.@+-]", name)
    if invalid_chars:
        simbols = " ".join(set(invalid_chars))
        raise ValidationError(
            "Имя пользователя содержит недопустимые символы: " f"{simbols}"
        )
