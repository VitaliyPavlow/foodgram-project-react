import csv
import inspect

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Менеджмент-команда для импорта из csv-файлов в базу данных.
    Пример использования в командной строке:
    python manage.py import_csv Ingredient ../data/ingredients.csv
    Ingredient - модель, в которую импортируем.
    ../data/ingredients.csv - путь где находится csv-файл.
    """

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Model name")
        parser.add_argument("csv_file", type=str, help="CSV file path")

    def handle(self, *args, **kwargs):
        model_name = kwargs["model"]
        csv_file_path = kwargs["csv_file"]

        model_class = apps.get_model("recipe", model_name)

        if not model_class:
            self.stdout.write(
                self.style.ERROR(f"Такой модели - {model_name} не найдено.")
            )
            return

        with open(csv_file_path, encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            rows = []
            for row in csv_reader:
                rows.append(model_class(**row))

            model_class.objects.bulk_create(rows)

        self.stdout.write(self.style.SUCCESS("Данные успешно импортированы."))


models = []

for model in apps.get_models():
    if not inspect.isabstract(model):
        models.append(model)

Command.models = models
