# 📚 Мануал: Подключение к Flibusta через Tor с obfs4 мостами

## 🎯 Назначение

Этот мануал описывает настройку и использование системы для доступа к библиотеке Flibusta через Tor с obfs4 мостами. Система позволяет:

- Безопасно подключаться к onion-адресу Flibusta
- Обходить блокировки с помощью obfs4 мостов
- Искать и загружать книги через API
- Получать метаданные книг в различных форматах

## ⚠️ ВАЖНО: НИКОГДА НЕ УДАЛЯТЬ!

Эта конфигурация критически важна для работы системы. Все файлы и настройки должны быть сохранены!

## 🔧 Компоненты системы

### 1. Основные файлы конфигурации

#### `/backend/books/external_config.py`
```python
# Конфигурация Tor SOCKS прокси для Tor Browser (порт 9150)
TOR_PROXY_CONFIG = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# Конфигурация Flibusta
FLIBUSTA_CONFIG = {
    'onion_url': 'http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion',
    'timeout': 30,
    'max_retries': 3
}
```

#### `/backend/books/external_sources.py`
- Класс `FlibustaTorClient` для работы с Tor
- Методы поиска книг через OPDS
- Парсинг метаданных и ссылок на скачивание

### 2. API эндпоинты

#### Поиск книг
```
POST /api/books/search_external/

Параметры:
{
    "query": "фантастика",
    "sources": ["flibusta"],
    "use_tor": true,
    "limit": 10
}
```

#### Получение категорий
```
GET /api/books/books/flibusta_categories/
```

#### Импорт книги
```
POST /api/books/import_external/

Параметры:
{
    "book_data": {...},
    "source": "flibusta"
}
```

## 🌐 Настройка Tor с obfs4 мостами

### 1. Используемые obfs4 мосты

```
obfs4 209.148.46.65:443 74FAD13168806246602538555B5521A0383A1875 cert=ssH+9rP8dG2NLDN2XuFw63hIO/9MNNinLmxQDpVa+7kTOa9/m+tGWT1SmSYpQ9uTBGa6Hw iat-mode=0
obfs4 51.222.13.177:80 5EDAC3B810E12B01F6FD8050D2FD3E277B289A08 cert=2uplIpLQ0q9+0qMFrK5pkaYRDOe460LL9WHBvatgkuRr/SL31wBOEupaMMJ6koRE6Ld0ew iat-mode=0
obfs4 193.11.166.194:27025 1AE2C08904527FEA90C4C4F8C1083EA59FBC6FAF cert=ItvYZzW5tn6v3G4UnQa6Qz04Npro6e81AP70YujmK/KXwDFPTs3aHXcHp4n8Vt6w/bv8cA iat-mode=0
obfs4 146.57.248.225:22 10A6CD36A537FCE513A322361547444B393989F0 cert=K1gDtDAIcUfeLqbstggjIw2rtgIKqdIhUlHp82XRqNSq/mtAjp1BIC9vHKJ2FAEpGssTPw iat-mode=0
obfs4 45.145.95.6:27015 C5B7CD6946FF10C5B3E89691A7D3F2C122D2117C cert=TD7PbUO0/0k6xYHMPW3vJxICfkMZNdkRrb63Zhl5j9dW3iRGiCx0A7mPhe5T2EDzQ35+Zw iat-mode=0
obfs4 192.95.36.142:443 CDF2E852BF539B82BD10E27E9115A31734E378C2 cert=qUVQ0srL1JI/vO6V6m/24anYXiJD3QP2HgzUKQtQ7GRqqUvs7P+tG43RtAqdhLOALP7DJQ iat-mode=1
obfs4 85.31.186.98:443 011F2599C0E9B27EE74B353155E244813763C3E5 cert=ayq0XzCwhpdysn5o0EyDUbmSOx3X/oTEbzDMvczHOdBJKlvIdHHLJGkZARtT4dcBFArPPg iat-mode=0
obfs4 37.218.245.14:38224 D9A82D2F9C2F65A18407B1D2B764F130847F8B5D cert=bjRaMrr1BRiAW8IE9U5z27fQaYgOhX1UCmOpg2pFpoMvo6ZgQMzLsaTzzQNTlm7hNcb+Sg iat-mode=0
obfs4 193.11.166.194:27020 86AC7B8D430DAC4117E9F42C9EAED18133863AAF cert=0LDeJH4JzMDtkJJrFphJCiPqKx7loozKN7VNfuukMGfHO0Z8OGdzHVkhVAOfo1mUdv9cMg iat-mode=0
obfs4 85.31.186.26:443 91A6354697E6B02A386312F68D82CF86824D3606 cert=PBwr+S8JTVZo6MPdHnkTwXJPILWADLqfMGoVvhZClMq/Urndyd42BwX9YFJHZnBB3H0XCw iat-mode=0
obfs4 193.11.166.194:27015 2D82C2E354D531A68469ADF7F878FA6060C6BACA cert=4TLQPJrTSaDffMK7Nbao6LC7G9OW/NHkUwIdjLSS3KYf0Nv4/nQiiI8dY2TcsQx01NniOg iat-mode=0
```

### 2. Настройка Tor Browser

1. Установить Tor Browser
2. Настроить obfs4 мосты в настройках
3. Запустить Tor Browser (SOCKS прокси на порту 9150)
4. Проверить подключение: `netstat -an | grep 9150`

## 🚀 Инструкция по запуску

### 1. Запуск Tor Browser
```bash
# Запуск Tor Browser на macOS
open -a "Tor Browser"

# Проверка, что порт 9150 слушается
netstat -an | grep 9150
```

### 2. Запуск Django сервера
```bash
cd /Users/aleksandrkocergin/Documents/kpit.pw/reader/backend
python manage.py runserver
```

### 3. Тестирование подключения
```bash
# Запуск тестового скрипта
python test_tor_import.py
```

## 📋 Примеры использования

### 1. Поиск книг через API
```python
import requests

data = {
    'query': 'фантастика',
    'sources': ['flibusta'],
    'use_tor': True,
    'limit': 5
}

response = requests.post('http://localhost:8000/api/books/search_external/', json=data)
books = response.json()
```

### 2. Получение метаданных книги
```python
# Пример ответа API
{
    "flibusta": [
        {
            "title": "Современная зарубежная фантастика-1",
            "author": "Гэлли Бен",
            "description": "",
            "updated": "2025-08-05T08:53:25+02:00",
            "download_links": [
                {
                    "format": "fb2+zip",
                    "url": "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/b/835269/fb2",
                    "type": "application/fb2+zip"
                },
                {
                    "format": "epub",
                    "url": "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/b/835269/epub",
                    "type": "application/epub+zip"
                }
            ]
        }
    ]
}
```

## 🔍 Диагностика и устранение неполадок

### 1. Проверка статуса Tor
```bash
# Проверка, что Tor Browser запущен
netstat -an | grep 9150

# Должен показать:
# tcp4  0  0  127.0.0.1.9150  *.*  LISTEN
```

### 2. Проверка подключения к onion-адресу
```bash
# Тест через curl
curl --socks5-hostname 127.0.0.1:9150 http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion
```

### 3. Проверка API
```bash
# Тест поиска
curl -X POST http://localhost:8000/api/books/search_external/ \
  -H "Content-Type: application/json" \
  -d '{"query": "тест", "sources": ["flibusta"], "use_tor": true, "limit": 1}'
```

## 📁 Структура файлов

```
backend/
├── books/
│   ├── external_config.py      # Конфигурация Tor и Flibusta
│   ├── external_sources.py     # Основная логика работы с Tor
│   ├── cover_sources.py        # Получение обложек
│   ├── views.py               # API эндпоинты
│   └── urls.py                # URL маршруты
├── test_tor_import.py         # Тестовый скрипт
└── TOR_FLIBUSTA_MANUAL.md     # Этот мануал
```

## ⚡ Производительность

- **Время подключения**: 2-5 секунд через obfs4 мосты
- **Скорость поиска**: 1-3 секунды на запрос
- **Поддерживаемые форматы**: fb2, epub, txt, html, rtf, mobi
- **Максимальный лимит результатов**: 50 книг за запрос

## 🛡️ Безопасность

- Все запросы идут через Tor с obfs4 мостами
- Используется SOCKS5h прокси для DNS резолвинга через Tor
- Onion-адреса обеспечивают end-to-end шифрование
- Никакие данные не логируются в открытом виде

## 📝 Логи и мониторинг

### Важные логи Django:
```
[05/Aug/2025 06:53:28] "POST /api/books/search_external/ HTTP/1.1" 200 1423
```

### Предупреждения (не критичные):
- `NotOpenSSLWarning` от urllib3 - не влияет на функциональность
- SSL ошибки при получении обложек - обложки получаются из других источников

## 🔄 Обновление мостов

Если мосты перестают работать:
1. Получить новые obfs4 мосты с https://bridges.torproject.org/
2. Обновить конфигурацию в Tor Browser
3. Перезапустить Tor Browser
4. Протестировать подключение

## 📞 Поддержка

При возникновении проблем:
1. Проверить статус Tor Browser
2. Проверить логи Django сервера
3. Запустить тестовый скрипт `test_tor_import.py`
4. Проверить доступность мостов

---

**Дата создания**: 5 августа 2025  
**Версия**: 1.0  
**Статус**: ✅ Протестировано и работает  

**⚠️ КРИТИЧЕСКИ ВАЖНО: НЕ УДАЛЯТЬ ЭТОТ МАНУАЛ И СВЯЗАННЫЕ ФАЙЛЫ!**