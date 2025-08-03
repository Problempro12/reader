# Reader - Система геймификации чтения книг

## Описание
Reader - это веб-приложение для мотивации к чтению через геймификацию. Система позволяет отслеживать прогресс чтения, получать награды за достижения и соревноваться с другими читателями.

## Основные возможности
- Управление личной библиотекой книг
- Отслеживание прогресса чтения
- Система достижений и наград
- Статистика чтения
- Профили пользователей

## Технологии
- **Backend**: Django + Django REST Framework
- **Frontend**: Vue.js 3 + Vite + TypeScript
- **База данных**: SQLite (разработка) / PostgreSQL (продакшн)
- **Аутентификация**: JWT

## Структура проекта

### Backend
Проект разделен на несколько приложений Django:

- **users** - управление пользователями, аутентификация
- **books** - модели книг, авторов и прогресса чтения
- **achievements** - система достижений и наград

### Модели данных

#### Пользователи (users)
- **User** - расширенная модель пользователя с дополнительными полями

#### Книги (books)
- **Author** - информация об авторе книги
- **Book** - информация о книге
- **UserBook** - связь между пользователем и книгой с указанием статуса (чтение, прочитано, запланировано, брошено)
- **ReadingProgress** - отметки о прогрессе чтения

#### Достижения (achievements)
- **Achievement** - типы достижений
- **UserAchievement** - полученные пользователем достижения

## Установка и запуск

### Backend
1. Создайте и активируйте виртуальное окружение:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Примените миграции:
```bash
python manage.py migrate
```

4. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

5. Запустите сервер:
```bash
python manage.py runserver
```

### Frontend
1. Установите зависимости:
```bash
cd frontend
npm install
```

2. Запустите сервер разработки:
```bash
npm run dev
```

## Доступ к приложению
- Backend API: http://localhost:8000/api/
- Frontend: http://localhost:5173/
- Админ-панель: http://localhost:8000/admin/

## API Endpoints

### Пользователи
- `POST /api/users/register/` - регистрация нового пользователя
- `POST /api/users/token/` - получение JWT токена
- `GET /api/users/me/` - информация о текущем пользователе

### Книги
- `GET /api/books/books/` - список всех книг
- `GET /api/books/books/{id}/` - детальная информация о книге
- `GET /api/books/authors/` - список всех авторов
- `GET /api/books/authors/{id}/` - детальная информация об авторе

### Книги пользователя
- `GET /api/books/user-books/` - список книг пользователя
- `POST /api/books/user-books/` - добавление книги в библиотеку пользователя
- `PATCH /api/books/user-books/{id}/` - обновление статуса книги

### Прогресс чтения
- `GET /api/books/reading-progress/` - история прогресса чтения
- `POST /api/books/reading-progress/` - добавление новой отметки о прогрессе

### Достижения
- `GET /api/achievements/achievements/` - список всех достижений
- `GET /api/achievements/user-achievements/` - достижения пользователя

### Импорт книг
- `POST /api/books/run-import-script/` - запуск импорта книг из Google Books API. Требует передачи параметра `query` в теле запроса для поиска книг. Для полноценной работы необходимо установить переменную окружения `GOOGLE_BOOKS_API_KEY` в файле `backend/books/utils.py`.

## Разработка

### Создание миграций
```bash
python manage.py makemigrations
```

### Применение миграций
```bash
python manage.py migrate
```

### Запуск тестов
```bash
python manage.py test
```

## Лицензия
MIT