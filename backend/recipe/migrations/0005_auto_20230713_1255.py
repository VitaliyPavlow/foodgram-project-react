# Generated by Django 3.2 on 2023-07-13 09:55

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipe", "0004_auto_20230712_1132"),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="is_favorited",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="is_in_shopping_cart",
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="recipe",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shoppinng_cart",
                to="recipe.recipe",
            ),
        ),
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shoppinng_cart",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                default="Anonymous",
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=8,
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Количество",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favored_by",
                to="recipe.recipe",
                verbose_name="Рецепт в избранном",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite"
            ),
        ),
    ]
