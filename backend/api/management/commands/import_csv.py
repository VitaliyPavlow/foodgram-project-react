import csv

from django.core.management.base import BaseCommand

from recipe.models import Ingredient


models = [Ingredient]


class Command(BaseCommand):
    """
    Менеджмент-команда для импорта из csv-файлов в базу данных.
    Пример использования в командной строке:
    python manage.py import_csv Genre static/data/genre.csv
    Genre - модель, в которую импортируем.
    static/data/genre.csv - путь где находится csv-файл
    Перед импортом убедитесь, что первая строчка
    csv-файла содержит названия полей модели.
    """

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Model name")
        parser.add_argument("csv_file", type=str, help="CSV file path")

    def handle(self, *args, **kwargs):
        model_name = kwargs["model"]
        csv_file_path = kwargs["csv_file"]

        model_class = None
        for m in models:
            if m.__name__.lower() == model_name.lower():
                model_class = m
                break

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

        self.stdout.write(self.style.SUCCESS("Data imported successfully"))
