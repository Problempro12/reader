#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/aleksandrkocergin/Documents/kpit.pw/reader/backend')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

try:
    from books.external_sources import search_external_books
    print("Модуль external_sources успешно импортирован")
    
    # Тестируем поиск
    print("Тестируем поиск книг...")
    results = search_external_books("Пушкин", ["flibusta"], use_tor=True, limit=2)
    print(f"Результаты поиска: {results}")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()