from autoslug import AutoSlugField
from unidecode import unidecode

from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .validators import hex_color_validator


MAX_LENGTH_TAG_NAME = 50
MAX_LENGTH_TAG_COLOR = 7
MAX_LENGTH_RECIPE_NAME = 100
MAX_LENGTH_INGREDIENT_NAME = 100
MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT = 100


class Tag(models.Model):
    """Модель Тэга."""

    name = models.CharField("Тэг", max_length=MAX_LENGTH_TAG_NAME, unique=True)
    color = models.CharField(
        max_length=MAX_LENGTH_TAG_COLOR,
        unique=True,
        validators=[hex_color_validator],
    )
    slug = AutoSlugField("Слаг", populate_from="name", unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def save(self, *args, **kwargs):
        self.slug = unidecode(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        related_name="recipes",
        verbose_name="Автор",
        default="Anonymous",
    )
    name = models.CharField("Рецепт", max_length=MAX_LENGTH_RECIPE_NAME)
    image = models.ImageField("Изображение", upload_to="recipes/images/")
    text = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        "Ingredient", through="RecipeIngredient"
    )
    tags = models.ManyToManyField("Tag", related_name="recipes")
    cooking_time = models.PositiveBigIntegerField("Время приготовления")
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppinng_cart",
        default=None,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppinng_cart",
        default=None,
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"Пользователь {self.user.first_name} {self.user.last_name} добавил рецепт {self.recipe} в список покупок."


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        "Ингредиент", max_length=MAX_LENGTH_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        "Единица измерения", max_length=MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredient"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(
        "Количество",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("ingredient",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.recipe.name}: {self.ingredient.name} {self.amount} {self.ingredient.measurement_unit}."


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favored_by",
        verbose_name="Рецепт в избранном",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"Рецепт {self.recipe.name} в избранном у пользователя {self.user.first_name} {self.user.last_name}."
