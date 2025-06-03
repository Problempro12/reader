# Система геймификации чтения книг

## Описание
Система для мотивации детей к чтению через геймификацию. Позволяет отслеживать прогресс чтения, получать награды и соревноваться с другими читателями.

## Технологии
- Backend: Django + Django REST Framework
- Frontend: Vue.js 3 + Vite
- База данных: PostgreSQL
- ORM: Prisma

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

3. Создайте файл .env:
```bash
cp .env.example .env
```

4. Настройте переменные окружения в .env:
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=reader
DB_USER=reader
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_URL=http://localhost:3000
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Запустите сервер:
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
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Админ-панель: http://localhost:8000/admin 

## Работа с базой данных

Для открытия графического интерфейса Prisma Studio выполните:

```bash
# Добавляем путь к исполняемым файлам Python в PATH
export PATH=$PATH:$HOME/Library/Python/3.9/bin

# Переходим в директорию backend
cd backend

# Запускаем Prisma Studio
prisma studio
```

Prisma Studio откроется в браузере и позволит удобно просматривать и редактировать данные в вашей базе данных.

Если команда `prisma` не найдена, убедитесь что:
1. Prisma установлен: `pip3 install prisma`
2. Путь к исполняемым файлам Python добавлен в PATH
3. Вы находитесь в директории `backend` 