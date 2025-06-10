# Документация бэкенда

## Содержание
1. [Общая информация](#общая-информация)
2. [Установка и настройка](#установка-и-настройка)
3. [API Endpoints](#api-endpoints)
4. [Модели данных](#модели-данных)
5. [Аутентификация](#аутентификация)
6. [Обработка ошибок](#обработка-ошибок)
7. [Структура файлов](#структура-файлов)
8. [Работа с базой данных: рекомендации и примеры](#работа-с-базой-данных-рекомендации-и-примеры)

## Общая информация

Бэкенд построен на Django REST Framework с использованием Prisma ORM для работы с базой данных. API предоставляет функционал для управления книгами, пользователями, голосованиями и прогрессом чтения.

### Технологии
- Python 3.8+
- Django 4.2+
- Django REST Framework
- Prisma ORM
- JWT Authentication

## Установка и настройка

1. Убедитесь, что у вас установлен Python 3.9 или выше.
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   ```
3. Активируйте виртуальное окружение:
   - На Windows:
     ```bash
     venv\Scripts\activate
     ```
   - На macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

5. Настройте переменные окружения в файле `.env`:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
SECRET_KEY="your-secret-key"
DEBUG=True
```

6. Примените миграции:
```bash
python manage.py migrate
```

## Запуск сервера

1. Перейдите в директорию бэкенда:
   ```bash
   cd backend
   ```
2. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Аутентификация

#### Регистрация пользователя
```
POST /api/users/register/
```
Тело запроса:
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password"
}
```
Ответ:
```json
{
    "message": "Пользователь успешно зарегистрирован",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username"
    }
}
```

#### Вход пользователя
```
POST /api/users/login/
```
Тело запроса:
```json
{
    "email": "user@example.com",
    "password": "password"
}
```
Ответ:
```json
{
    "refresh": "refresh_token",
    "access": "access_token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username"
    }
}
```

### Книги

#### Получение списка книг
```
GET /api/books/
```
Заголовки:
```
Authorization: Bearer <access_token>
```
Ответ:
```json
[
    {
        "id": 1,
        "title": "Название книги",
        "author": "Автор",
        "genre": "Жанр",
        "ageCategory": "Возрастная категория"
    }
]
```

#### Создание книги
```
POST /api/books/
```
Заголовки:
```
Authorization: Bearer <access_token>
```
Тело запроса:
```json
{
    "title": "Название книги",
    "author": "Автор",
    "genre": "Жанр",
    "ageCategory": "Возрастная категория"
}
```

#### Получение информации о книге
```
GET /api/books/{id}/
```
Заголовки:
```
Authorization: Bearer <access_token>
```

### Голосования

#### Создание голоса
```
POST /api/books/vote/
```
Заголовки:
```
Authorization: Bearer <access_token>
```
Тело запроса:
```json
{
    "bookId": 1
}
```

### Прогресс чтения

#### Создание записи о прогрессе
```
POST /api/books/progress/
```
Заголовки:
```
Authorization: Bearer <access_token>
```
Тело запроса:
```json
{
    "bookId": 1,
    "marks": 1
}
```

## Модели данных

### User
- id: UUID
- email: String (unique)
- username: String (unique)
- is_premium: Boolean
- is_staff: Boolean
- is_superuser: Boolean

### Book
- id: UUID
- title: String
- author: String
- genre: Genre (relation)
- ageCategory: AgeCategory (relation)

### Vote
- id: UUID
- userId: User (relation)
- bookId: Book (relation)
- weekNumber: Integer

### ReadingProgress
- id: UUID
- userId: User (relation)
- bookId: Book (relation)
- weekNumber: Integer
- marks: Integer

## Аутентификация

API использует JWT (JSON Web Tokens) для аутентификации. Каждый запрос должен содержать заголовок:
```
Authorization: Bearer <access_token>
```

Токены имеют ограниченный срок действия:
- Access Token: 5 минут
- Refresh Token: 24 часа

Для обновления токена используйте endpoint:
```
POST /api/users/token/refresh/
```
Тело запроса:
```json
{
    "refresh": "refresh_token"
}
```

## Обработка ошибок

API возвращает следующие коды состояния:
- 200: Успешный запрос
- 201: Успешное создание
- 400: Неверный запрос
- 401: Не авторизован
- 403: Доступ запрещен
- 404: Ресурс не найден
- 500: Внутренняя ошибка сервера

Пример ответа с ошибкой:
```json
{
    "error": "Описание ошибки",
    "details": {
        "field": ["Описание проблемы с полем"]
    }
}
```

## Безопасность

1. Все пароли хешируются перед сохранением
2. API защищено от CSRF атак
3. Реализована защита от брутфорс атак
4. Все чувствительные данные передаются через HTTPS

## Мониторинг и логирование

Система использует встроенное логирование Django. Логи доступны в:
- development.log
- production.log

Для мониторинга производительности рекомендуется использовать:
- Django Debug Toolbar (для разработки)
- Sentry (для продакшена)

## API

### Профиль пользователя

- **GET /api/users/profile/**: Получить профиль текущего пользователя.
- **PATCH /api/users/profile/**: Обновить профиль пользователя.

### Медиа-файлы

- **GET /api/media/<path:path>**: Получить медиа-файл по указанному пути.

## Тестирование

Для запуска тестов выполните:
```bash
python manage.py test
```

## Дополнительная информация

- Для проверки проекта на наличие ошибок используйте:
  ```bash
  python manage.py check
  ```
- Для создания новых миграций:
  ```bash
  python manage.py makemigrations
  ```

## Структура файлов

- **manage.py**: Основной скрипт для управления Django-проектом.
- **requirements.txt**: Список зависимостей проекта.
- **.env**: Файл с переменными окружения (не включен в репозиторий).
- **reader/**: Основная директория проекта.
  - **settings.py**: Настройки Django-проекта.
  - **urls.py**: Основные URL-маршруты проекта.
  - **wsgi.py**: Конфигурация WSGI для развертывания.
  - **asgi.py**: Конфигурация ASGI для асинхронного развертывания.
- **reader/views.py**: Содержит представления (views) для API.
- **reader/urls.py**: URL-маршруты для API.
- **reader/models.py**: Определения моделей данных.
- **reader/serializers.py**: Сериализаторы для API.
- **reader/tests.py**: Тесты для приложения.
- **reader/migrations/**: Директория с миграциями базы данных.
- **static/**: Директория для статических файлов.
- **media/**: Директория для загруженных медиа-файлов.

## Полезные команды

### Управление пользователями
```bash
# Создание суперпользователя
python manage.py createsuperuser

# Создание обычного пользователя через shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@example.com', 'password')
```

### Управление базой данных
```bash
# Создание новых миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Откат последней миграции
python manage.py migrate app_name zero

# Просмотр SQL для миграции
python manage.py sqlmigrate app_name migration_number

# Очистка базы данных
# 1. Удалить все данные из всех таблиц
python manage.py flush

# 2. Удалить все данные из конкретного приложения
python manage.py shell
>>> from django.apps import apps
>>> from django.db import connection
>>> app_models = apps.get_app_config('app_name').get_models()
>>> for model in app_models:
...     model.objects.all().delete()

# 3. Сбросить базу данных (удалить и создать заново)
# Для PostgreSQL:
dropdb db_name
createdb db_name
python manage.py migrate

# Для SQLite:
rm db.sqlite3
python manage.py migrate

# Работа с Prisma Studio
# Запуск Prisma Studio (графический интерфейс)
prisma studio

# Запуск Prisma Studio на определенном порту
prisma studio --port 5555

# Запуск Prisma Studio с определенной схемой
prisma studio --schema=./prisma/schema.prisma
```

### Управление статическими файлами
```bash
# Сборка статических файлов
python manage.py collectstatic

# Очистка статических файлов
python manage.py collectstatic --clear
```

### Отладка и тестирование
```bash
# Запуск тестов
python manage.py test

# Запуск тестов с подробным выводом
python manage.py test -v 2

# Запуск тестов конкретного приложения
python manage.py test app_name

# Запуск сервера разработки
python manage.py runserver

# Запуск сервера на определенном порту
python manage.py runserver 8080

# Запуск сервера на всех интерфейсах
python manage.py runserver 0.0.0.0:8000
```

### Управление проектом
```bash
# Проверка проекта на наличие ошибок
python manage.py check

# Создание нового приложения
python manage.py startapp app_name

# Создание проекта
django-admin startproject project_name

# Создание приложения в проекте
python manage.py startapp app_name
```

### Работа с shell
```bash
# Запуск Django shell
python manage.py shell

# Запуск shell с автоматической загрузкой моделей
python manage.py shell_plus  # требует django-extensions
```

### Управление переводами
```bash
# Создание файлов перевода
python manage.py makemessages -l ru

# Компиляция файлов перевода
python manage.py compilemessages
```

### Очистка базы данных от лишних таблиц

```bash
# 1. Удалить все миграции (кроме __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 2. Удалить базу данных
dropdb db_name

# 3. Создать новую базу данных
createdb db_name

# 4. Создать новые миграции
python manage.py makemigrations

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser
```

### Удаление записей с учетом внешних ключей

```bash
# Через Django shell
python manage.py shell

# Удаление с учетом зависимостей
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute('SET FOREIGN_KEY_CHECKS=0;')  # Отключаем проверку внешних ключей
>>> # Удаляем записи
>>> cursor.execute('DELETE FROM table_name;')
>>> cursor.execute('SET FOREIGN_KEY_CHECKS=1;')  # Включаем проверку обратно
```

## Работа с базой данных: рекомендации и примеры

### 1. Стандартный рабочий цикл с миграциями

- После изменения моделей:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- Не редактируйте миграции вручную.
- Храните миграции в git.

### 2. Резервное копирование и восстановление

- **Создать бэкап:**
  ```bash
  pg_dump db_name > backup.sql
  ```
- **Восстановить из бэкапа:**
  ```bash
  psql db_name < backup.sql
  ```

### 3. Корректное удаление данных

- Для удаления связанных данных используйте методы моделей с учётом внешних ключей (`on_delete=models.CASCADE` и т.д.).
- Для полной очистки:
  ```bash
  python manage.py flush
  ```
- Для удаления только определённых записей:
  ```python
  # В Django shell
  from books.models import Book
  Book.objects.filter(title='Название').delete()
  ```

### 4. Работа с Prisma Studio/pgAdmin

- **Prisma Studio:**
  ```bash
  prisma studio
  ```
- **pgAdmin:**
  - Установите pgAdmin (https://www.pgadmin.org/download/)
  - Подключитесь к вашей базе и работайте с таблицами через GUI

### 5. Откат миграций

- Откатить последнее изменение:
  ```bash
  python manage.py migrate app_name <номер_предыдущей_миграции>
  ```
- Откатить все миграции приложения:
  ```bash
  python manage.py migrate app_name zero
  ```

### 6. Добавление новых полей/таблиц

- Добавьте поле/таблицу в models.py
- Выполните:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### 7. Тестирование изменений в БД

- Пишите тесты для моделей в файле `tests.py` вашего приложения.
- Пример:
  ```python
  from django.test import TestCase
  from books.models import Book

  class BookModelTest(TestCase):
      def test_create_book(self):
          book = Book.objects.create(title='Тест', author='Автор')
          self.assertEqual(Book.objects.count(), 1)
  ```

### 8. Документируйте структуру и процессы

- Описывайте структуру моделей и связи в README или Wiki.
- Фиксируйте нестандартные решения и типовые команды.

---

**Если вы работаете в команде — обязательно согласуйте правила работы с миграциями и резервным копированием!** 