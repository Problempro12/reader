#!/usr/bin/env python3
"""
Скрипт для реального импорта книг фантастики из Флибусты
"""

import os
import sys
import django
import requests
import json
from typing import List, Dict, Any

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient
from books.models import Book, Author
from django.db import transaction

def find_fantasy_category_url() -> str:
    """Находит URL категории фантастики"""
    print("🔍 Поиск категории фантастики...")
    
    client = FlibustaTorClient(use_tor=False)
    categories = client.browse_categories()
    
    # Ищем категорию "По жанрам"
    genres_category = None
    for category in categories:
        if any(keyword in category['name'].lower() for keyword in ['жанр', 'genre']):
            genres_category = category
            print(f"📂 Найдена категория жанров: {category['name']}")
            break
    
    if not genres_category:
        raise Exception("Категория жанров не найдена")
    
    # Получаем жанры
    genre_items = client._get_categories_from_catalog(genres_category['url'], limit=100)
    
    # Ищем фантастику
    for item in genre_items:
        title = item.get('title', '').lower()
        if any(keyword in title for keyword in ['фэнтези', 'fantasy', 'фантаст']):
            print(f"🎯 Найден жанр: {item.get('title')}")
            return item.get('download_url') or item.get('url')
    
    raise Exception("Жанр фантастики не найден")

def import_fantasy_books(limit: int = 10) -> List[Dict[str, Any]]:
    """Импортирует книги фантастики"""
    print(f"📚 Начинаем импорт {limit} книг фантастики...\n")
    
    try:
        # Находим URL категории фантастики
        fantasy_url = find_fantasy_category_url()
        
        # Получаем книги
        client = FlibustaTorClient(use_tor=False)
        books = client.browse_books_by_category(fantasy_url, sort_by_popularity=True, limit=limit)
        
        if not books:
            print("❌ Книги не найдены")
            return []
        
        print(f"📖 Найдено {len(books)} книг для импорта\n")
        
        imported_books = []
        
        with transaction.atomic():
            for i, book_data in enumerate(books, 1):
                print(f"📖 {i}/{len(books)}. Импорт: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                
                try:
                    # Проверяем, есть ли уже такая книга
                    existing_book = Book.objects.filter(
                        title=book_data.get('title', ''),
                        author__name=book_data.get('author', '')
                    ).first()
                    
                    if existing_book:
                        print(f"   ⚠️  Книга уже существует в базе (ID: {existing_book.id})")
                        continue
                    
                    # Создаем или получаем автора
                    author_name = book_data.get('author', 'Неизвестный автор')
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={'bio': ''}
                    )
                    
                    if created:
                        print(f"   👤 Создан новый автор: {author_name}")
                    
                    # Загружаем полную информацию о книге
                    print(f"   📥 Загрузка содержимого и обложки...")
                    full_book_data = client.get_book_details(book_data.get('id'))
                    
                    # Создаем книгу с полным содержимым
                    book = Book.objects.create(
                        title=book_data.get('title', 'Без названия'),
                        author=author,
                        description=book_data.get('description', ''),
                        content=full_book_data.get('content', ''),
                        cover_url=full_book_data.get('cover_url', ''),
                        genre='Фантастика'
                    )
                    
                    imported_books.append({
                        'id': book.id,
                        'title': book.title,
                        'author': book.author.name,
                        'genre': book.genre
                    })
                    
                    print(f"   ✅ Книга импортирована (ID: {book.id})")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка импорта: {e}")
                    continue
        
        print(f"\n🎉 Импорт завершен! Импортировано {len(imported_books)} книг")
        return imported_books
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return []

def main():
    """Основная функция"""
    print("=== Реальный импорт книг фантастики ===\n")
    
    # Проверяем подключение к базе данных
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Подключение к базе данных установлено\n")
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return
    
    # Импортируем книги
    imported_books = import_fantasy_books(limit=3)
    
    if imported_books:
        print("\n📋 Импортированные книги:")
        for book in imported_books:
            print(f"   • {book['title']} - {book['author']} (ID: {book['id']})")
        
        print(f"\n💡 Всего в базе книг: {Book.objects.count()}")
        print(f"💡 Всего авторов: {Author.objects.count()}")
    
    print("\n✅ Импорт завершен!")

if __name__ == '__main__':
    main()