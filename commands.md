# Команды для запуска проекта

## Запуск бэкенда (Django)

```bash
# Переходим в папку backend
cd backend

# Активируем виртуальное окружение
source venv/bin/activate  # для Mac/Linux
# или
.\venv\Scripts\activate  # для Windows

# Запускаем сервер
python manage.py runserver
```

## Запуск фронтенда (Vue.js)

```bash
# Переходим в папку frontend
cd frontend

# Запускаем dev-сервер
npm run dev
```

## Полезные команды для разработки

### Бэкенд
```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### Фронтенд
```bash
# Установка зависимостей
npm install

# Сборка проекта
npm run build

# Проверка линтером
npm run lint
``` 