import os

from autoslug import AutoSlugField
from unidecode import unidecode

from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .validators import hex_color_validator


MAX_LENGTH_TAG_NAME = 50
MAX_LENGTH_TAG_COLOR = 7
MAX_LENGTH_RECIPE_NAME = 200
MAX_LENGTH_INGREDIENT_NAME = 100
MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT = 100


class Tag(models.Model):
    name = models.CharField("Тэг", max_length=MAX_LENGTH_TAG_NAME, unique=True)
    color = models.CharField(
        max_length=MAX_LENGTH_TAG_COLOR,
        unique=True,
        validators=[hex_color_validator],
        verbose_name="Цвет",
    )
    slug = AutoSlugField("Слаг", populate_from="name", unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = unidecode(self.name)
        return super().save(*args, **kwargs)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        related_name="recipes",
        verbose_name="Автор",
        default=1,
    )
    name = models.CharField("Рецепт", max_length=MAX_LENGTH_RECIPE_NAME)
    image = models.ImageField("Изображение", upload_to="recipes/images/")
    text = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
        related_name="recipe",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        "Tag", related_name="recipes", verbose_name="Тэги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления", validators=[MinValueValidator(5)]
    )
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.image:
            os.remove(self.image.path)
        super().delete(*args, **kwargs)


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        default=None,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        default=None,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return (
            f"Пользователь {self.user.first_name} {self.user.last_name}"
            f" добавил рецепт {self.recipe} в список покупок."
        )


class Ingredient(models.Model):
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
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredient",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="recipe_ingredient",
        verbose_name="Ингредиент в рецепте",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("ingredient",)
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="uq_recipe_ingredient",
            )
        ]

    def __str__(self):
        return (
            f"{self.recipe.name}: {self.ingredient.name}"
            f" {self.amount} {self.ingredient.measurement_unit}."
        )


class Favorite(models.Model):
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
                fields=["user", "recipe"], name="uq_user_recipe"
            )
        ]

    def __str__(self):
        return (
            f"Рецепт {self.recipe.name} в избранном у "
            f"пользователя {self.user.first_name} {self.user.last_name}."
        )
