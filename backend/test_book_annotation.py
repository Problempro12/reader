#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/aleksandrkocergin/Documents/kpit.pw/reader/backend')

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import ExternalBookSources

def test_book_annotation():
    """Тестирование получения аннотации книги"""
    
    # ID книги из предоставленного HTML
    book_id = "836962"
    
    print(f"Тестирование получения аннотации для книги с ID: {book_id}")
    print("=" * 60)
    
    try:
        # Создаем клиент для работы с внешними источниками
        external_sources = ExternalBookSources(use_tor_for_flibusta=True)
        
        # Получаем аннотацию
        print("Получение аннотации...")
        description = external_sources.get_book_description(book_id)
        
        if description:
            print("\nАннотация найдена:")
            print("-" * 40)
            print(description)
            print("-" * 40)
            print(f"\nДлина аннотации: {len(description)} символов")
        else:
            print("\nАннотация не найдена или пуста")
            
    except Exception as e:
        print(f"Ошибка при получении аннотации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_book_annotation()