#!/usr/bin/env python
"""
Тест новой системы получения обложек для книг из Flibusta с поддержкой flibusta.su
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books
from books.cover_sources import get_book_cover_url
import json

def test_new_cover_system():
    """Тест новой системы обложек с поддержкой flibusta.su"""
    print("=== Тест новой системы получения обложек с поддержкой flibusta.su ===\n")
    
    try:
        # Ищем книги в Flibusta
        print("🔍 Поиск книг в Flibusta...")
        results = search_external_books('Пушкин', limit=3, use_tor=False)
        flibusta_books = results.get('flibusta', [])
        
        print(f"📚 Найдено книг в Flibusta: {len(flibusta_books)}\n")
        
        for i, book in enumerate(flibusta_books):
            print(f"📖 Книга {i+1}:")
            print(f"  Название: {book.get('title')}")
            print(f"  Автор: {book.get('author')}")
            print(f"  Источник: {book.get('source')}")
            print(f"  ID книги: {book.get('source_id', 'Не найден')}")
            
            cover_url = book.get('cover_url')
            print(f"  Обложка: {cover_url}")
            
            # Дополнительная проверка - пытаемся получить обложку напрямую с ID
            title = book.get('title')
            author = book.get('author')
            book_id = book.get('source_id')
            
            if title and author:
                # Проверка с ID
                direct_cover = get_book_cover_url(title, author, book_id)
                print(f"  Прямая проверка обложки (с ID {book_id}): {direct_cover}")
                
                # Проверка без ID (старый способ)
                direct_cover_no_id = get_book_cover_url(title, author)
                print(f"  Прямая проверка обложки (без ID): {direct_cover_no_id}")
                
                # Анализ улучшений
                if (direct_cover != '/placeholder-book.svg' and 
                    direct_cover_no_id == '/placeholder-book.svg'):
                    print(f"  🎉 Обложка найдена благодаря flibusta.su (ID: {book_id})!")
                elif (direct_cover != direct_cover_no_id and 
                      'flibusta.su' in direct_cover):
                    print(f"  🎉 Обложка получена с flibusta.su вместо внешних источников!")
            
            if cover_url and cover_url != '/placeholder-book.svg':
                print(f"  ✅ Реальная обложка найдена!")
                
                # Проверяем, откуда обложка
                if 'googleapis.com' in cover_url:
                    print(f"  📚 Источник обложки: Google Books")
                elif 'covers.openlibrary.org' in cover_url:
                    print(f"  📚 Источник обложки: Open Library")
                elif 'flibusta.su' in cover_url:
                    print(f"  📚 Источник обложки: Flibusta.su")
                elif 'flibusta' in cover_url:
                    print(f"  📚 Источник обложки: Flibusta")
                else:
                    print(f"  📚 Источник обложки: Неизвестный")
            else:
                print(f"  ⚠️ Используется заглушка")
            
            print()
        
        # Дополнительный тест - прямое получение обложки
        print("\n🧪 Дополнительный тест прямого получения обложки:")
        test_title = "Евгений Онегин"
        test_author = "Пушкин"
        
        print(f"Ищем обложку для: '{test_title}' автор '{test_author}'")
        direct_cover = get_book_cover_url(test_title, test_author)
        print(f"Результат (без ID): {direct_cover}")
        
        # Тест с фиктивным ID
        test_id = "12345"
        direct_cover_with_id = get_book_cover_url(test_title, test_author, test_id)
        print(f"Результат (с ID {test_id}): {direct_cover_with_id}")
        
        if direct_cover and direct_cover != '/placeholder-book.svg':
            print("✅ Прямое получение обложки работает!")
        else:
            print("⚠️ Прямое получение вернуло заглушку")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_new_cover_system()