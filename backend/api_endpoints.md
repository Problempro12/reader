# API Эндпоинты Backend

## Базовый URL
`http://localhost:8000/api/`

## Модуль Books

### BookViewSet
- `GET http://localhost:8000/api/books/books/` - Список всех книг
- `POST http://localhost:8000/api/books/books/` - Создать новую книгу (только админ)
- `GET http://localhost:8000/api/books/books/{id}/` - Получить книгу по ID
- `PUT http://localhost:8000/api/books/books/{id}/` - Обновить книгу (только админ)
- `PATCH http://localhost:8000/api/books/books/{id}/` - Частично обновить книгу (только админ)
- `DELETE http://localhost:8000/api/books/books/{id}/` - Удалить книгу (только админ)

#### Дополнительные действия BookViewSet:
- `GET http://localhost:8000/api/books/books/{id}/content/` - Получить содержимое книги
- `GET http://localhost:8000/api/books/books/top_voted/` - Топ книг по голосам
- `GET http://localhost:8000/api/books/books/user_votes/` - Книги, за которые голосовал пользователь (требует авторизации)
- `POST http://localhost:8000/api/books/books/run_import_script/` - Запустить скрипт импорта
- `POST http://localhost:8000/api/books/books/{id}/rate/` - Оценить книгу (требует авторизации)
- `GET http://localhost:8000/api/books/books/{id}/rating/` - Получить рейтинг книги
- `POST http://localhost:8000/api/books/books/{id}/vote/` - Проголосовать за книгу (требует авторизации)
- `DELETE http://localhost:8000/api/books/books/{id}/remove_vote/` - Убрать голос за книгу (требует авторизации)
- `GET http://localhost:8000/api/books/books/{id}/vote_info/` - Информация о голосах за книгу
- `GET http://localhost:8000/api/books/books/current_week/` - Книга недели
- `GET http://localhost:8000/api/books/books/top/` - Топ книг (популярные)
- `GET http://localhost:8000/api/books/books/recommended/` - Рекомендованные книги
- `GET http://localhost:8000/api/books/books/genres/` - Список жанров
- `GET http://localhost:8000/api/books/books/flibusta_categories/` - Категории Flibusta
- `GET http://localhost:8000/api/books/books/age_categories/` - Возрастные категории
- `GET http://localhost:8000/api/books/books/voting_candidates/` - Кандидаты для голосования

### AuthorViewSet
- `GET http://localhost:8000/api/books/authors/` - Список авторов
- `POST http://localhost:8000/api/books/authors/` - Создать автора (только админ)
- `GET http://localhost:8000/api/books/authors/{id}/` - Получить автора по ID
- `PUT http://localhost:8000/api/books/authors/{id}/` - Обновить автора (только админ)
- `PATCH http://localhost:8000/api/books/authors/{id}/` - Частично обновить автора (только админ)
- `DELETE http://localhost:8000/api/books/authors/{id}/` - Удалить автора (только админ)

### UserBookViewSet
- `GET http://localhost:8000/api/books/user-books/` - Библиотека пользователя (требует авторизации)
- `POST http://localhost:8000/api/books/user-books/` - Добавить книгу в библиотеку (требует авторизации)
- `GET http://localhost:8000/api/books/user-books/{id}/` - Получить книгу из библиотеки
- `PUT http://localhost:8000/api/books/user-books/{id}/` - Обновить статус книги в библиотеке
- `PATCH http://localhost:8000/api/books/user-books/{id}/` - Частично обновить книгу в библиотеке
- `DELETE http://localhost:8000/api/books/user-books/{id}/` - Удалить книгу из библиотеки

#### Дополнительные действия UserBookViewSet:
- `POST http://localhost:8000/api/books/user-books/add_to_library/` - Добавить книгу в библиотеку
- `POST http://localhost:8000/api/books/user-books/{id}/update_status/` - Обновить статус книги

### ReadingProgressViewSet
- `GET http://localhost:8000/api/books/reading-progress/` - Прогресс чтения пользователя (требует авторизации)
- `POST http://localhost:8000/api/books/reading-progress/` - Создать запись прогресса (требует авторизации)
- `GET http://localhost:8000/api/books/reading-progress/{id}/` - Получить запись прогресса
- `PUT http://localhost:8000/api/books/reading-progress/{id}/` - Обновить прогресс
- `PATCH http://localhost:8000/api/books/reading-progress/{id}/` - Частично обновить прогресс
- `DELETE http://localhost:8000/api/books/reading-progress/{id}/` - Удалить запись прогресса

### Внешние источники
- `POST http://localhost:8000/api/books/search-external/` - Поиск книг во внешних источниках
- `POST http://localhost:8000/api/books/import-external/` - Импорт книги из внешнего источника (требует авторизации)

### Дополнительные эндпоинты
- `GET http://localhost:8000/api/books/book-list/` - Список книг для админки

## Модуль Users

### Регистрация и профиль
- `POST http://localhost:8000/api/users/register/` - Регистрация пользователя
- `GET http://localhost:8000/api/users/profile/` - Получить профиль пользователя (требует авторизации)
- `PUT http://localhost:8000/api/users/profile/` - Обновить профиль пользователя (требует авторизации)
- `PATCH http://localhost:8000/api/users/profile/` - Частично обновить профиль (требует авторизации)
- `DELETE http://localhost:8000/api/users/profile/` - Удалить профиль пользователя (требует авторизации)

### Книги пользователя
- `GET http://localhost:8000/api/users/books/` - Книги пользователя с фильтрацией по статусу (требует авторизации)

## Модуль Achievements

### AchievementViewSet
- `GET http://localhost:8000/api/achievements/achievements/` - Список достижений (требует авторизации)
- `POST http://localhost:8000/api/achievements/achievements/` - Создать достижение (только админ)
- `GET http://localhost:8000/api/achievements/achievements/{id}/` - Получить достижение по ID (требует авторизации)
- `PUT http://localhost:8000/api/achievements/achievements/{id}/` - Обновить достижение (только админ)
- `PATCH http://localhost:8000/api/achievements/achievements/{id}/` - Частично обновить достижение (только админ)
- `DELETE http://localhost:8000/api/achievements/achievements/{id}/` - Удалить достижение (только админ)

### UserAchievementViewSet
- `GET http://localhost:8000/api/achievements/user-achievements/` - Достижения пользователя (требует авторизации)
- `GET http://localhost:8000/api/achievements/user-achievements/{id}/` - Получить достижение пользователя по ID

### Проверка достижений
- `POST http://localhost:8000/api/achievements/check/` - Проверить и присвоить достижения (требует авторизации)

## Аутентификация (JWT)

### Стандартные эндпоинты JWT
- `POST http://localhost:8000/api/token/` - Получить токены доступа и обновления
- `POST http://localhost:8000/api/token/refresh/` - Обновить токен доступа
- `POST http://localhost:8000/api/token/verify/` - Проверить токен

## Параметры запросов

### Для списка книг (`/api/books/books/`)
- `page` - номер страницы
- `limit` - количество элементов на странице
- `search` - поиск по названию и автору
- `genre` - фильтр по жанру
- `age_category` - фильтр по возрастной категории

### Для книг пользователя (`/api/users/books/`)
- `status` - фильтр по статусу (planned, reading, completed, dropped)

## Статусы книг в библиотеке пользователя
- `planned` - Запланировано к прочтению
- `reading` - Читаю сейчас
- `completed` - Прочитано
- `dropped` - Брошено

## Форматы ответов

Все API возвращают JSON. Успешные ответы содержат данные, ошибки содержат поле `error` с описанием.

### Пример успешного ответа для списка книг:
```json
{
  "books": [...],
  "total": 100,
  "page": 1,
  "limit": 10
}
```

### Пример ответа с ошибкой:
```json
{
  "error": "Описание ошибки"
}
```

## Права доступа

- **AllowAny** - доступно всем
- **IsAuthenticated** - требует авторизации
- **IsAdminUser** - только для администраторов
- **IsAdminOrReadOnly** - чтение для всех, изменение только для админов

## Примеры для тестирования (готовые URL)

### Основные эндпоинты для демонстрации:
- `http://localhost:8000/api/books/books/` - Список всех книг
- `http://localhost:8000/api/books/books/1/` - Конкретная книга (ID=1)
- `http://localhost:8000/api/books/books/genres/` - Список жанров
- `http://localhost:8000/api/books/books/flibusta_categories/` - Категории Flibusta
- `http://localhost:8000/api/books/books/top/` - Топ книг
- `http://localhost:8000/api/books/books/recommended/` - Рекомендованные книги
- `http://localhost:8000/api/books/authors/` - Список авторов
- `http://localhost:8000/api/achievements/achievements/` - Список достижений

### Для тестирования с параметрами:
- `http://localhost:8000/api/books/books/?page=1&limit=5` - Первые 5 книг
- `http://localhost:8000/api/books/books/?search=фантастика` - Поиск по слову "фантастика"

---

*Этот файл создан автоматически на основе анализа кода.*