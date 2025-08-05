#!/usr/bin/env python
"""
Импорт книг через поиск с полным содержимым и обложками
"""

import os
import sys
import django
from typing import List, Dict, Any
from django.db import transaction

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book, Author
from books.external_sources import FlibustaTorClient
from books.cover_sources import get_book_cover_url

def import_books_by_search(search_queries: List[str], limit_per_query: int = 2) -> List[Dict[str, Any]]:
    """Импортирует книги через поиск с полным содержимым"""
    print(f"📚 Начинаем импорт книг через поиск...\n")
    
    try:
        client = FlibustaTorClient(use_tor=False)
        all_books = []
        
        # Поиск по каждому запросу
        for query in search_queries:
            print(f"🔍 Поиск: '{query}'")
            books = client.search_books(query, limit=limit_per_query * 3)  # Берем больше для фильтрации
            
            if books:
                print(f"📖 Найдено {len(books)} книг по запросу '{query}'")
                all_books.extend(books[:limit_per_query])  # Берем только нужное количество
            else:
                print(f"❌ Книги по запросу '{query}' не найдены")
        
        if not all_books:
            print("❌ Книги не найдены ни по одному запросу")
            return []
        
        print(f"\n📖 Всего найдено {len(all_books)} книг для импорта\n")
        
        imported_books = []
        
        with transaction.atomic():
            for i, book_data in enumerate(all_books, 1):
                print(f"📖 {i}/{len(all_books)}. Импорт: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                
                try:
                    # Проверяем, есть ли уже такая книга
                    existing_book = Book.objects.filter(
                        title=book_data.get('title', ''),
                        author__name=book_data.get('author', '')
                    ).first()
                    
                    if existing_book:
                        print(f"   ⚠️  Книга уже существует (ID: {existing_book.id})")
                        continue
                    
                    # Получаем полные данные книги с содержимым
                    print(f"   📥 Загружаем полное содержимое...")
                    content = client.download_book(book_data, format_preference='fb2')
                    
                    if not content:
                        print(f"   ❌ Не удалось загрузить содержимое")
                        continue
                    
                    # Создаем или получаем автора
                    author_name = book_data.get('author', 'Неизвестный автор')
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={'bio': f'Автор книги "{book_data.get("title", "")}"'}
                    )
                    
                    if created:
                        print(f"   👤 Создан новый автор: {author_name}")
                    
                    # Получаем обложку для книги
                    cover_url = get_book_cover_url(
                        book_data.get('title', 'Без названия'),
                        author.name,
                        book_data.get('source_id')
                    )
                    
                    # Создаем книгу с полным содержимым
                    book = Book.objects.create(
                        title=book_data.get('title', 'Без названия'),
                        author=author,
                        description=book_data.get('description', ''),
                        content=content or '',
                        cover_url=cover_url,
                        genre='Художественная литература'
                    )
                    
                    imported_books.append({
                        'id': book.id,
                        'title': book.title,
                        'author': book.author.name,
                        'has_content': bool(book.content),
                        'has_cover': bool(book.cover_url)
                    })
                    
                    print(f"   ✅ Импортирована (ID: {book.id})")
                    print(f"      Содержимое: {'Да' if book.content else 'Нет'}")
                    print(f"      Обложка: {'Да' if book.cover_url else 'Нет'}")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка импорта книги: {e}")
                    continue
        
        print(f"\n✅ Импорт завершен! Импортировано {len(imported_books)} новых книг")
        
        if imported_books:
            print("\n📋 Импортированные книги:")
            for book in imported_books:
                print(f"   • {book['title']} - {book['author']} (ID: {book['id']})")
        
        return imported_books
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return []

if __name__ == '__main__':
    print("=== Импорт книг через поиск с содержимым ===")
    print()
    
    # Проверяем подключение к базе данных
    try:
        Book.objects.count()
        print("✅ Подключение к базе данных установлено")
        print()
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        sys.exit(1)
    
    # Список поисковых запросов
    search_queries = [
        "Толкин",
        "Стругацкие",
        "Азимов",
        "Лукьяненко",
        "Желязны"
    ]
    
    # Импортируем книги
    imported_books = import_books_by_search(search_queries, limit_per_query=1)
    
    print(f"\n🎉 Готово! Импортировано {len(imported_books)} книг")