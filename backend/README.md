# Документация бэкенда

## Содержание
1. [Общая информация](#общая-информация)
2. [Установка и настройка](#установка-и-настройка)
3. [API Endpoints](#api-endpoints)
4. [Модели данных](#модели-данных)
5. [Аутентификация](#аутентификация)
6. [Обработка ошибок](#обработка-ошибок)

## Общая информация

Бэкенд построен на Django REST Framework с использованием Prisma ORM для работы с базой данных. API предоставляет функционал для управления книгами, пользователями, голосованиями и прогрессом чтения.

### Технологии
- Python 3.8+
- Django 4.2+
- Django REST Framework
- Prisma ORM
- JWT Authentication

## Установка и настройка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения в файле `.env`:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
SECRET_KEY="your-secret-key"
DEBUG=True
```

4. Примените миграции:
```bash
python manage.py migrate
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