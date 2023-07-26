import re

from django.core.exceptions import ValidationError


def hex_color_validator(value):
    HEX_COLOR_REGEX = "^#([A-Fa-f0-9]{6})$"
    if not re.match(HEX_COLOR_REGEX, value):
        raise ValidationError("Введите корректный HEX-код цвета")
