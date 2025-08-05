#!/usr/bin/env python3
"""
Скрипт для импорта книг научной фантастики из Флибусты с полным содержимым и обложками
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

def find_scifi_category_url() -> str:
    """Находит URL любой подходящей категории книг"""
    print("🔍 Поиск подходящей категории книг...")
    
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
    
    # Показываем доступные жанры для отладки
    print("📋 Доступные жанры:")
    for i, item in enumerate(genre_items[:10]):
        print(f"   {i+1}. {item.get('title', 'Без названия')}")
    
    # Ищем любой подходящий жанр (детективы, приключения, роман)
    for item in genre_items:
        title = item.get('title', '').lower()
        if any(keyword in title for keyword in ['детектив', 'приключен', 'роман', 'проза', 'классик']):
            print(f"🎯 Найден жанр: {item.get('title')}")
            return item.get('url')
    
    raise Exception("Подходящий жанр не найден")

def import_scifi_books(limit: int = 5) -> List[Dict[str, Any]]:
    """Импортирует книги с полным содержимым"""
    print(f"📚 Начинаем импорт {limit} книг с полным содержимым...\n")
    
    try:
        # Находим URL подходящей категории
        category_url = find_scifi_category_url()
        
        # Получаем книги
        client = FlibustaTorClient(use_tor=False)
        books = client.browse_books_by_category(category_url, sort_by_popularity=True, limit=50)  # Увеличиваем лимит поиска
        
        if not books:
            print("❌ Книги не найдены в этой категории")
            # Попробуем другую категорию - найдем любую с книгами
            print("🔄 Пробуем найти другие категории...")
            
            # Получаем все категории заново
            categories = client.browse_categories()
            genres_category = None
            for cat in categories:
                if 'жанр' in cat.get('name', '').lower():
                    genres_category = cat
                    break
            
            if genres_category:
                genre_items = client._get_categories_from_catalog(genres_category['url'], limit=100)
                # Пробуем разные жанры
                for item in genre_items:
                    title = item.get('title', '').lower()
                    if any(keyword in title for keyword in ['классик', 'проза', 'роман', 'литература']):
                        print(f"🎯 Найден альтернативный жанр: {item.get('title')}")
                        books = client.browse_books_by_category(item.get('url'), sort_by_popularity=True, limit=50)
                        if books:
                            break
            
            if not books:
                print("❌ Книги не найдены ни в одной категории")
                return []
        
        print(f"📖 Найдено {len(books)} книг для проверки\n")
        
        imported_books = []
        imported_count = 0
        
        with transaction.atomic():
            for i, book_data in enumerate(books, 1):
                if imported_count >= limit:
                    break
                    
                print(f"📖 {i}/{len(books)}. Проверка: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                
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
                        genre='Художественная литература'
                    )
                    
                    imported_books.append({
                        'id': book.id,
                        'title': book.title,
                        'author': book.author.name,
                        'genre': book.genre,
                        'has_content': bool(book.content),
                        'has_cover': bool(book.cover_url),
                        'content_length': len(book.content) if book.content else 0
                    })
                    
                    imported_count += 1
                    print(f"   ✅ Книга импортирована (ID: {book.id})")
                    print(f"   📄 Содержимое: {'Есть' if book.content else 'Нет'} ({len(book.content) if book.content else 0} символов)")
                    print(f"   🖼️  Обложка: {'Есть' if book.cover_url else 'Нет'}")
                    
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
    print("=== Импорт книг научной фантастики с содержимым ===\n")
    
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
    imported_books = import_scifi_books(limit=3)
    
    if imported_books:
        print("\n📋 Импортированные книги:")
        for book in imported_books:
            print(f"   • {book['title']} - {book['author']} (ID: {book['id']})")
            print(f"     📄 Содержимое: {book['content_length']} символов")
            print(f"     🖼️  Обложка: {'Есть' if book['has_cover'] else 'Нет'}")
        
        print(f"\n💡 Всего в базе книг: {Book.objects.count()}")
        print(f"💡 Всего авторов: {Author.objects.count()}")
    
    print("\n✅ Импорт завершен!")

if __name__ == '__main__':
    main()