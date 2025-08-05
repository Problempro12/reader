# Работа с внешними источниками книг

Этот модуль предоставляет функциональность для поиска и скачивания книг из внешних источников, таких как Флибуста и LibGen.

## Настройка доступа к Флибусте

Система настроена для работы через собственный VPN без использования Tor прокси.

### Проверка доступа

```bash
# Проверка доступа к onion-адресу через VPN
curl http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion

# Проверка доступа к clearnet зеркалу
curl https://flibusta.is
```

## API Endpoints

### Поиск книг во внешних источниках

**GET** `/api/books/search_external/`

**Параметры:**
- `q` (обязательный) - поисковый запрос
- `use_tor` (опциональный) - использовать onion-адрес через VPN для доступа к Флибусте (по умолчанию `true`)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/books/search_external/?q=Толстой&use_tor=true"
```

**Пример ответа:**
```json
{
  "query": "Толстой",
  "results": {
    "flibusta": [
      {
        "title": "Война и мир",
        "author": "Лев Толстой",
        "description": "Роман-эпопея",
        "download_links": [
          {
            "format": "fb2",
            "url": "http://flibustahezeous3.onion/b/12345/download",
            "type": "application/fb2+xml"
          }
        ],
        "source": "flibusta",
        "source_id": "12345"
      }
    ],
    "libgen": []
  },
  "total_found": 1
}
```

### Импорт книги из внешнего источника

**POST** `/api/books/import_external/`

**Требует аутентификации**

**Параметры тела запроса:**
- `source` (обязательный) - источник книги (`flibusta` или `libgen`)
- `book_data` (обязательный) - данные книги, полученные из поиска
- `format` (опциональный) - предпочитаемый формат (по умолчанию `fb2`)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/books/import_external/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source": "flibusta",
    "format": "fb2",
    "book_data": {
      "title": "Война и мир",
      "author": "Лев Толстой",
      "description": "Роман-эпопея",
      "source_id": "12345",
      "download_links": [
        {
          "format": "fb2",
          "url": "http://flibustahezeous3.onion/b/12345/download"
        }
      ]
    }
  }'
```

**Пример ответа:**
```json
{
  "message": "Книга успешно импортирована",
  "book": {
    "id": 123,
    "title": "Война и мир",
    "author": "Лев Толстой",
    "description": "Роман-эпопея"
  },
  "added_to_library": true
}
```

## Конфигурация

### Переменные окружения

Вы можете настроить работу модуля через переменные окружения:

```bash
# Настройки Tor прокси
EXTERNAL_BOOKS_TOR_PROXY_HTTP=socks5h://127.0.0.1:9050
EXTERNAL_BOOKS_TOR_PROXY_HTTPS=socks5h://127.0.0.1:9050

# Настройки Флибусты
EXTERNAL_BOOKS_FLIBUSTA_TIMEOUT=30
EXTERNAL_BOOKS_FLIBUSTA_MAX_RETRIES=3

# Общие настройки
EXTERNAL_BOOKS_MAX_FILE_SIZE=52428800  # 50MB
EXTERNAL_BOOKS_DEFAULT_TIMEOUT=30
```

### Настройки Django

В `settings.py` можно добавить:

```python
EXTERNAL_BOOKS_CONFIG = {
    'flibusta': {
        'timeout': 30,
        'max_retries': 3,
        'supported_formats': ['fb2', 'epub', 'mobi', 'txt', 'pdf']
    },
    'general': {
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'encoding_detection': True
    },
    'security': {
        'verify_ssl': True,
        'rate_limit': {
            'requests_per_minute': 30
        }
    }
}
```

## Поддерживаемые форматы

### Флибуста
- FB2 (FictionBook 2.0)
- EPUB
- MOBI
- TXT
- PDF

### LibGen
- PDF
- EPUB
- DJVU
- MOBI

## Безопасность и ограничения

1. **Размер файлов**: Максимальный размер скачиваемого файла - 50MB
2. **Rate limiting**: Ограничение на количество запросов в минуту
3. **Таймауты**: Настраиваемые таймауты для предотвращения зависания
4. **Кодировки**: Автоматическое определение кодировки для текстовых файлов
5. **VPN**: Использование собственного VPN для доступа к .onion сайтам

## Устранение неполадок

### Ошибки доступа к Флибусте

1. Проверьте доступность .onion адреса через VPN:
   ```bash
   curl http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion
   ```

2. Попробуйте альтернативные clearnet зеркала:
   ```bash
   curl https://flibusta.is
   curl https://flibusta.lib
   curl https://flisland.net
   ```

3. Убедитесь, что VPN подключен и работает корректно

### Установка зависимостей

```bash
pip install requests[socks] beautifulsoup4 lxml chardet
```

## Новые API эндпоинты для работы с категориями

### Получение списка категорий

**GET** `/api/books/browse_categories/`

**Параметры запроса:**
- `use_tor` (опциональный) - использовать onion-адрес через VPN (по умолчанию `true`)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/books/browse_categories/?use_tor=false"
```

**Пример ответа:**
```json
{
  "categories": [
    {
      "name": "Жанры",
      "url": "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genres"
    },
    {
      "name": "Категории", 
      "url": "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/categories"
    }
  ],
  "total_found": 2
}
```

### Получение книг из категории

**GET** `/api/books/browse_category_books/`

**Параметры запроса:**
- `category_url` (обязательный) - URL категории из предыдущего запроса
- `use_tor` (опциональный) - использовать Tor (по умолчанию `true`)
- `sort_by_popularity` (опциональный) - сортировать по популярности (по умолчанию `true`)
- `limit` (опциональный) - количество книг (по умолчанию `50`)

**Пример запроса:**
```bash
curl "http://localhost:8000/api/books/browse_category_books/?category_url=http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genres&sort_by_popularity=true&limit=10"
```

### Массовый импорт книг из категории

**POST** `/api/books/import_category_books/`

**Требует аутентификации**

**Параметры тела запроса:**
- `category_url` (обязательный) - URL категории
- `use_tor` (опциональный) - использовать Tor (по умолчанию `true`)
- `sort_by_popularity` (опциональный) - сортировать по популярности (по умолчанию `true`)
- `limit` (опциональный) - количество книг для импорта (по умолчанию `50`)
- `format` (опциональный) - предпочитаемый формат (по умолчанию `fb2`)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/books/import_category_books/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "category_url": "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genres/fantasy",
    "sort_by_popularity": true,
    "limit": 20,
    "format": "fb2"
  }'
```

**Пример ответа:**
```json
{
  "message": "Импорт завершен. Успешно: 18, Ошибок: 2",
  "imported_count": 18,
  "failed_count": 2,
  "imported_books": [
    {
      "id": 123,
      "title": "Властелин колец",
      "author": "Дж. Р. Р. Толкин"
    }
  ]
}
```

## Примеры использования в коде

```python
from books.external_sources import search_external_books, import_book_from_external_source, FlibustaTorClient

# Поиск книг
results = search_external_books("Пушкин", use_tor=True)
print(f"Найдено книг: {len(results['flibusta'])}")

# Импорт книги
if results['flibusta']:
    book_data = results['flibusta'][0]
    content = import_book_from_external_source('flibusta', book_data, 'fb2')
    if content:
        print("Книга успешно импортирована")

# Работа с категориями
client = FlibustaTorClient(use_tor=True)

# Получение категорий
categories = client.browse_categories()
print(f"Найдено категорий: {len(categories)}")

# Получение книг из категории с сортировкой по популярности
if categories:
    category_url = categories[0]['url']
    books = client.browse_books_by_category(category_url, sort_by_popularity=True, limit=10)
    print(f"Найдено популярных книг: {len(books)}")
```

## Лицензия и ответственность

⚠️ **Важно**: Использование данного модуля для доступа к защищенному авторским правом контенту может нарушать законодательство вашей страны. Используйте только для доступа к книгам, находящимся в общественном достоянии или с разрешения правообладателей.

Разработчики не несут ответственности за неправомерное использование данного программного обеспечения.