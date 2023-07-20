import re

from django.core.exceptions import ValidationError


# Валидатор пропускает цветовой код из 6 и 3 знаков.
# В ТЗ точно не указано с каким кодом работает фронтэнд.
def hex_color_validator(value):
    HEX_COLOR_REGEX = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.match(HEX_COLOR_REGEX, value):
        raise ValidationError("Введите корректный HEX-код цвета")
