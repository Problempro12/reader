# Настройка автоматического выбора книги недели

Для автоматического выбора книги недели каждый понедельник в 00:00 по московскому времени, необходимо настроить cron задачу.

## Способ 1: Использование crontab (Linux/macOS)

1. Откройте crontab для редактирования:
```bash
crontab -e
```

2. Добавьте следующую строку:
```bash
# Выбор книги недели каждый понедельник в 00:00 по МСК (UTC+3)
0 21 * * 0 cd /path/to/your/project/backend && /path/to/your/venv/bin/python manage.py select_book_of_week
```

**Примечание:** Время указано как 21:00 UTC (воскресенье), что соответствует 00:00 понедельника по МСК.

## Способ 2: Использование systemd timer (Linux)

1. Создайте файл сервиса `/etc/systemd/system/book-of-week.service`:
```ini
[Unit]
Description=Select Book of the Week
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/your/project/backend
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/python manage.py select_book_of_week
```

2. Создайте файл таймера `/etc/systemd/system/book-of-week.timer`:
```ini
[Unit]
Description=Run Book of the Week selection weekly
Requires=book-of-week.service

[Timer]
# Каждый понедельник в 00:00 по МСК
OnCalendar=Mon *-*-* 00:00:00
Timezone=Europe/Moscow
Persistent=true

[Install]
WantedBy=timers.target
```

3. Включите и запустите таймер:
```bash
sudo systemctl enable book-of-week.timer
sudo systemctl start book-of-week.timer
```

## Способ 3: Использование Django-crontab (рекомендуется для Django проектов)

1. Установите django-crontab:
```bash
pip install django-crontab
```

2. Добавьте в `settings.py`:
```python
INSTALLED_APPS = [
    # ... другие приложения
    'django_crontab',
]

CRONJOBS = [
    ('0 21 * * 0', 'books.management.commands.select_book_of_week.Command', [], {'timezone': 'UTC'}),
]
```

3. Добавьте cron задачи:
```bash
python manage.py crontab add
```

## Способ 4: Использование Celery Beat (для продакшена)

1. Установите Celery:
```bash
pip install celery redis
```

2. Создайте задачу в `books/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def select_book_of_week_task():
    call_command('select_book_of_week')
```

3. Настройте периодические задачи в `settings.py`:
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'select-book-of-week': {
        'task': 'books.tasks.select_book_of_week_task',
        'schedule': crontab(hour=21, minute=0, day_of_week=0),  # Воскресенье 21:00 UTC = Понедельник 00:00 МСК
    },
}
```

## Ручной запуск

Для ручного запуска команды выбора книги недели:
```bash
cd backend
python manage.py select_book_of_week
```

## Проверка работы

Для проверки, что команда работает корректно:
1. Убедитесь, что в базе данных есть книги с голосами
2. Запустите команду вручную
3. Проверьте, что создалась запись в таблице `WeeklyBook`
4. Проверьте, что у выбранной книги сбросились голоса и установился флаг `is_book_of_week=True`

## Логирование

Рекомендуется настроить логирование для отслеживания работы команды:
```python
# В settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/path/to/logs/book_of_week.log',
        },
    },
    'loggers': {
        'books.management.commands.select_book_of_week': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```