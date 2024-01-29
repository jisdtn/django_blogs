### Платформа для блогов

Социальная сеть, где пользователи могут создавать посты, комментировать посты других авторов. 

```commandline
Реализован backend на Django, написаны юнит-тесты, добавлена возможность прикреплять картинки, добавлены страниы ошибок, проведен рефакторинг, добавлен django-debug-toolbar.
```
### Запуск проекта в dev-режиме:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/jisdtn/django_blogs
```

```
cd django_blogs
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить backend проекта:

```
python3 manage.py runserver
```
### Примеры запросов к API.

```commandline
http://localhost/api/cats/ ('GET')
```
```commandline
http://localhost/api/cats/ ('POST')
```
```commandline
http://localhost/api/achievements/ ('GET')
```
