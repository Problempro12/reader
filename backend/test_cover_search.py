#!/usr/bin/env python
"""
Тест поиска обложек для конкретных книг
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.cover_sources import get_book_cover_url
from books.models import Book

def test_cover_search():
    print("=== Тест поиска обложек ===")
    print()
    
    # Тестируем поиск обложек для известных книг
    test_books = [
        ("1984", "Джордж Оруэлл"),
        ("Властелин колец", "Толкин"),
        ("Гарри Поттер и философский камень", "Роулинг"),
        ("Война и мир", "Толстой"),
        ("Мастер и Маргарита", "Булгаков"),
        ("Атлант расправил плечи", "Айн Рэнд"),
    ]
    
    for title, author in test_books:
        print(f"🔍 Поиск обложки для: '{title}' - {author}")
        cover_url = get_book_cover_url(title, author)
        
        if cover_url == '/placeholder-book.svg':
            print(f"   📋 Результат: заглушка (обложка не найдена)")
        else:
            print(f"   ✅ Результат: {cover_url}")
            
            # Определяем источник
            if 'googleapis.com' in cover_url:
                print(f"   📚 Источник: Google Books")
            elif 'covers.openlibrary.org' in cover_url:
                print(f"   📚 Источник: Open Library")
            elif 'flibusta' in cover_url:
                print(f"   📚 Источник: Flibusta")
            else:
                print(f"   📚 Источник: неизвестный")
        
        print()
    
    # Проверяем книги из нашей базы данных
    print("📖 Проверка книг из базы данных:")
    print()
    
    recent_books = Book.objects.all().order_by('-id')[:5]
    for book in recent_books:
        print(f"🔍 Книга: '{book.title}' - {book.author.name}")
        print(f"   Текущая обложка: {book.cover_url}")
        
        # Попробуем найти лучшую обложку
        new_cover = get_book_cover_url(book.title, book.author.name)
        if new_cover != book.cover_url:
            print(f"   🆕 Альтернативная обложка: {new_cover}")
        else:
            print(f"   ✅ Обложка актуальна")
        print()

if __name__ == '__main__':
    test_cover_search()