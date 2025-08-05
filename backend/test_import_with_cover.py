#!/usr/bin/env python
"""
Тест импорта книги из Flibusta с проверкой обложки
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books
from books.models import Book, Author
from django.contrib.auth.models import User
import json

def test_import_with_cover():
    """Тест импорта книги с проверкой обложки"""
    print("=== Тест импорта книги из Flibusta с обложкой ===")
    
    try:
        # Поиск книг
        results = search_external_books('Пушкин', limit=1, use_tor=False)
        flibusta_books = results.get('flibusta', [])
        
        if not flibusta_books:
            print("❌ Книги не найдены")
            return
            
        book_data = flibusta_books[0]
        print(f"📚 Найдена книга: {book_data.get('title')}")
        print(f"👤 Автор: {book_data.get('author')}")
        print(f"🖼️ Обложка: {book_data.get('cover_url')}")
        
        # Создаем или получаем автора
        author, created = Author.objects.get_or_create(
            name=book_data.get('author', 'Неизвестный автор')
        )
        
        # Создаем книгу
        book, created = Book.objects.get_or_create(
            title=book_data.get('title'),
            author=author,
            defaults={
                'description': book_data.get('description', ''),
                'content': 'Содержимое книги будет добавлено позже.',
                'cover_url': book_data.get('cover_url')
            }
        )
        
        if created:
            print(f"✅ Книга успешно создана с ID: {book.id}")
        else:
            print(f"ℹ️ Книга уже существует с ID: {book.id}")
            
        print(f"📖 Название: {book.title}")
        print(f"👤 Автор: {book.author.name}")
        print(f"🖼️ URL обложки: {book.cover_url}")
        
        # Проверяем, что обложка установлена
        if book.cover_url:
            if book.cover_url == '/placeholder-book.svg':
                print("✅ Заглушка обложки установлена корректно")
            else:
                print(f"✅ Обложка установлена: {book.cover_url}")
        else:
            print("❌ Обложка не установлена")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_import_with_cover()