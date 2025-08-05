#!/usr/bin/env python
"""
Тест проверки обложек в результатах поиска Flibusta
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books
import json

def test_covers():
    """Тест проверки обложек"""
    print("=== Тест проверки обложек в результатах поиска ===")
    
    try:
        results = search_external_books('Пушкин', limit=2, use_tor=False)
        flibusta_books = results.get('flibusta', [])
        
        print(f"Найдено книг: {len(flibusta_books)}")
        
        for i, book in enumerate(flibusta_books):
            print(f"\n📚 Книга {i+1}:")
            print(f"  Название: {book.get('title')}")
            print(f"  Автор: {book.get('author')}")
            print(f"  Поля книги: {list(book.keys())}")
            print(f"  Cover URL: {book.get('cover_url')}")
            
            if book.get('cover_url'):
                print(f"  ✅ Обложка найдена: {book.get('cover_url')}")
            else:
                print(f"  ❌ Обложка отсутствует")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_covers()