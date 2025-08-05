# 🚀 БЫСТРЫЙ ЗАПУСК: Tor + Flibusta

## ⚡ Пошаговая инструкция запуска

### 1. Запуск Tor Browser
```bash
# Запустить Tor Browser
open -a "Tor Browser"

# Подождать 30-60 секунд для подключения к мостам
# Проверить, что порт 9150 активен:
netstat -an | grep 9150
# Должно показать: tcp4  0  0  127.0.0.1.9150  *.*  LISTEN
```

### 2. Запуск Django сервера
```bash
cd /Users/aleksandrkocergin/Documents/kpit.pw/reader/backend
python manage.py runserver
```

### 3. Тестирование (в новом терминале)
```bash
# Быстрый тест поиска
curl -X POST http://localhost:8000/api/books/search_external/ \
  -H "Content-Type: application/json" \
  -d '{"query": "фантастика", "sources": ["flibusta"], "use_tor": true, "limit": 3}'
```

## 📋 Готовые API запросы

### Поиск книг
```bash
curl -X POST http://localhost:8000/api/books/search_external/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Стругацкие",
    "sources": ["flibusta"],
    "use_tor": true,
    "limit": 5
  }'
```

### Получение категорий
```bash
curl http://localhost:8000/api/books/books/flibusta_categories/
```

## 🔧 Устранение проблем

### Tor не подключается:
1. Перезапустить Tor Browser
2. Подождать 1-2 минуты
3. Проверить порт: `netstat -an | grep 9150`

### API возвращает ошибки:
1. Убедиться, что Tor Browser запущен
2. Проверить логи Django сервера
3. Попробовать другой поисковый запрос

### Медленная работа:
- Это нормально для Tor с мостами
- Обычное время ответа: 2-10 секунд

## 📁 Важные файлы

- `TOR_FLIBUSTA_MANUAL.md` - Полный мануал
- `TOR_CONFIG_BACKUP/` - Резервные копии
- `backend/books/external_config.py` - Основная конфигурация

## ⚠️ ПОМНИТЕ

- **НЕ УДАЛЯТЬ** файлы конфигурации
- Tor Browser должен быть запущен **ПЕРЕД** использованием API
- Система работает только с onion-адресом Flibusta
- Все запросы идут через obfs4 мосты для обхода блокировок

---

**Статус**: ✅ Протестировано 5 августа 2025  
**Версия**: 1.0