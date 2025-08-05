#!/usr/bin/env python
"""
Скрипт для исправления обложек книг из Flibusta
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book

def fix_flibusta_covers():
    """Исправляет обложки для книг из Flibusta"""
    print("=== Исправление обложек книг из Flibusta ===")
    
    # Находим все книги без обложек или с пустыми обложками
    books_without_covers = Book.objects.filter(
        cover_url__isnull=True
    ) | Book.objects.filter(
        cover_url=''
    )
    
    print(f"Найдено книг без обложек: {books_without_covers.count()}")
    
    updated_count = 0
    
    for book in books_without_covers:
        # Устанавливаем заглушку обложки
        book.cover_url = '/placeholder-book.svg'
        book.save()
        updated_count += 1
        print(f"✅ Обновлена книга: {book.title} (ID: {book.id})")
    
    print(f"\n🎉 Обновлено книг: {updated_count}")
    
    # Проверяем результат
    remaining_without_covers = Book.objects.filter(
        cover_url__isnull=True
    ) | Book.objects.filter(
        cover_url=''
    )
    
    print(f"Осталось книг без обложек: {remaining_without_covers.count()}")

if __name__ == '__main__':
    fix_flibusta_covers()