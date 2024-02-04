# Сайт для обмена рецептами FOODGRAM.

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Стэк технологий

* Django 3
* Django Rest Framework
* Gunicorn
* Docker
* CI/CD
* Nginx

### Сайт проекта
https://food-gram.site
ip: 84.252.142.141 \n
*** сейчас проект не доступен в интернете, но его можно развернуть локально.

### Учетная запись администратора
username: admin
email: admin@admin.ru
password: 1234_4321q

### Установка
Клонировать репозиторий и перейти в него в командной строке:

```git@github.com:VitaliyPavlow/foodgram-project-react.git```

```cd backend```

Cоздать и активировать виртуальное окружение:

Команды для Windows:

```py -m venv venv```

```source venv/Scripts/activate```

Команды для Linux и macOS:

```python3 -m venv venv```

```source venv/bin/activate``` 
 

Обновить пакетный менеджер pip:

```py -m pip install --upgrade pip``` - для Windows.

```python3 -m pip install --upgrade pip``` - для Linux и macOS.

Установить зависимости из файла requirements.txt:

```pip install -r requirements.txt```


Выполнить миграции:

```py manage.py migrate``` - для Windows.

```python3 manage.py migrate``` - для Linux и macOS.

Запустить проект:

```py manage.py runserver```- для Windows.

```python3 manage.py runserver``` - для Linux и macOS.
