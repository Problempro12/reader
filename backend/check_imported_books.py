#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book, Author

def check_imported_books():
    print("=== Проверка импортированных книг ===")
    print()
    
    # Общая статистика
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    fantasy_books = Book.objects.filter(genre='Фантастика').count()
    
    print(f"📊 Общая статистика:")
    print(f"   • Всего книг: {total_books}")
    print(f"   • Всего авторов: {total_authors}")
    print(f"   • Книг фантастики: {fantasy_books}")
    print()
    
    # Последние импортированные книги
    print("📚 Последние 5 книг в базе:")
    for book in Book.objects.all().order_by('-id')[:5]:
        print(f"   • {book.title} - {book.author.name} (жанр: {book.genre or 'не указан'})")
    print()
    
    # Книги фантастики
    print("🧙 Книги фантастики:")
    fantasy_books = Book.objects.filter(genre='Фантастика')
    for book in fantasy_books:
        print(f"   • {book.title} - {book.author.name}")
    print()
    
    print("✅ Проверка завершена!")

if __name__ == '__main__':
    check_imported_books()