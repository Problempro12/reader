# Руководство по обновлению описаний книг из Flibusta

Эта функциональность позволяет автоматически получать аннотации книг из Flibusta и обновлять поле `description` в базе данных.

## Новые возможности

### 1. Метод получения аннотации в FlibustaTorClient

```python
from books.external_sources import FlibustaTorClient

client = FlibustaTorClient(use_tor=True)
description = client.get_book_description("836962")  # ID книги в Flibusta
```

### 2. Метод в ExternalBookSources

```python
from books.external_sources import ExternalBookSources

sources = ExternalBookSources(use_tor_for_flibusta=True)
description = sources.get_book_description("836962")
```

### 3. Django команда для обновления описаний

#### Обновление конкретной книги по внешнему ID:
```bash
python manage.py update_book_descriptions --book-id 59 --external-id 836962 --force
```

#### Параметры команды:
- `--book-id` - ID книги в нашей базе данных
- `--external-id` - ID книги в Flibusta
- `--force` - принудительно обновить, даже если описание уже есть
- `--only-missing` - обновить только книги без описания

## Как это работает

1. **Парсинг HTML**: Метод `get_book_description` загружает HTML-страницу книги с Flibusta
2. **Извлечение аннотации**: Ищет заголовок `<h2>Аннотация</h2>` и извлекает текст из следующих элементов
3. **Очистка текста**: Удаляет лишние пробелы и переносы строк
4. **Возврат результата**: Возвращает очищенный текст аннотации

## Пример использования

```python
#!/usr/bin/env python
import os
import sys
import django

sys.path.append('/path/to/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book
from books.external_sources import ExternalBookSources

# Получаем книгу из базы
book = Book.objects.get(id=59)

# Получаем аннотацию из Flibusta
sources = ExternalBookSources(use_tor_for_flibusta=True)
description = sources.get_book_description("836962")

# Обновляем описание
if description:
    book.description = description
    book.save(update_fields=['description'])
    print(f"Описание обновлено: {len(description)} символов")
```

## Требования

- Tor должен быть запущен для доступа к Flibusta
- Корректный onion-адрес Flibusta в конфигурации
- Знание внешнего ID книги в Flibusta

## Ограничения

- Работает только с книгами, доступными на Flibusta
- Требует знания внешнего ID книги
- Зависит от структуры HTML-страниц Flibusta
- Может быть медленным из-за использования Tor

## Тестирование

Для тестирования функциональности используйте:

```bash
# Тест получения аннотации
python test_book_annotation.py

# Демонстрация полного процесса
python demo_description_update.py

# Обновление через Django команду
python manage.py update_book_descriptions --book-id 59 --external-id 836962
```