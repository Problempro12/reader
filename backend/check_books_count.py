#!/usr/bin/env python
"""
Проверка количества книг в базе данных
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book, Author

def check_books():
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    
    print(f"📚 Всего книг в БД: {total_books}")
    print(f"👤 Всего авторов в БД: {total_authors}")
    print()
    
    if total_books > 0:
        print("📖 Последние 10 книг:")
        for book in Book.objects.all().order_by('-id')[:10]:
            print(f"   ID: {book.id}, Title: {book.title}, Author: {book.author.name}")
    else:
        print("❌ Книги в базе данных не найдены")
    
    print()
    
    # Проверим книги с содержимым
    books_with_content = Book.objects.exclude(content='').count()
    print(f"📄 Книг с содержимым: {books_with_content}")
    
    # Проверим книги с обложками
    books_with_covers = Book.objects.exclude(cover_url='').count()
    print(f"🖼️  Книг с обложками: {books_with_covers}")

if __name__ == '__main__':
    check_books()