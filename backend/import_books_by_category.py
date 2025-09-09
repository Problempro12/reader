#!/usr/bin/env python
"""
Импорт книг по категории из Флибусты
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
from books.external_sources import FlibustaTorClient, ExternalBookSources, import_book_from_external_source

def import_books_by_category(category_url: str, count: int = 5) -> List[Dict[str, Any]]:
    """Импортирует книги из указанной категории"""
    print(f"📚 Начинаем импорт {count} книг из категории...\n")
    
    try:
        # Создаем клиенты
        client = FlibustaTorClient(use_tor=True)
        sources = ExternalBookSources(use_tor_for_flibusta=True)
        
        print(f"🔗 Получаем книги из категории: {category_url}")
        
        # Получаем книги из категории
        books_data = client.browse_books_by_category(category_url, sort_by_popularity=True, limit=count)
        
        if not books_data:
            print("❌ Книги в категории не найдены")
            return []
        
        print(f"📖 Найдено {len(books_data)} книг для импорта\n")
        
        imported_books = []
        imported_count = 0
        errors = []
        
        with transaction.atomic():
            for i, book_data in enumerate(books_data, 1):
                print(f"📖 {i}/{len(books_data)}. Импорт: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                
                try:
                    # Проверяем, есть ли уже такая книга
                    existing_book = Book.objects.filter(
                        title=book_data.get('title', ''),
                        author__name=book_data.get('author', '')
                    ).first()
                    
                    if existing_book:
                        print(f"   ⚠️  Книга уже существует (ID: {existing_book.id})")
                        continue
                    
                    # Создаем или получаем автора
                    author_name = book_data.get('author', 'Неизвестный автор')
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={'bio': ''}
                    )
                    
                    if created:
                        print(f"   👤 Создан новый автор: {author_name}")
                    
                    # Загружаем полное содержимое книги
                    print(f"   📥 Загружаем полное содержимое...")
                    content = import_book_from_external_source(book_data, 'flibusta', 'fb2', use_tor=True)
                    
                    if not content:
                        print(f"   ❌ Не удалось загрузить содержимое")
                        errors.append(f"Не удалось загрузить содержимое для '{book_data.get('title', 'Unknown')}'")
                        continue
                    
                    # Получаем аннотацию книги
                    description = book_data.get('description', '')
                    book_id = book_data.get('source_id') or book_data.get('id')
                    if book_id and not description:
                        try:
                            description = sources.get_book_description(book_id)
                        except:
                            pass  # Если не удалось получить описание, продолжаем без него
                    
                    # Создаем книгу с полным содержимым
                    book = Book.objects.create(
                        title=book_data.get('title', 'Без названия'),
                        author=author,
                        description=description or '',
                        content=content,
                        cover_url=book_data.get('cover_url', ''),
                        genre=book_data.get('genre', 'Общее'),
                        source_id=book_id or '',
                        source_type='flibusta'
                    )
                    
                    imported_books.append({
                        'id': book.id,
                        'title': book.title,
                        'author': book.author.name,
                        'has_content': bool(book.content),
                        'has_cover': bool(book.cover_url)
                    })
                    
                    imported_count += 1
                    print(f"   ✅ Импортирована (ID: {book.id})")
                    print(f"      Содержимое: {'Да' if book.content else 'Нет'}")
                    print(f"      Обложка: {'Да' if book.cover_url else 'Нет'}")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка импорта книги: {e}")
                    errors.append(f"Error importing '{book_data.get('title', 'Unknown')}': {str(e)}")
                    continue
                
                print()
        
        print(f"✅ Импорт завершен! Импортировано {imported_count} новых книг")
        
        if imported_books:
            print("\n📋 Импортированные книги:")
            for book in imported_books:
                print(f"   • {book['title']} - {book['author']} (ID: {book['id']})")
        
        if errors:
            print(f"\n⚠️  Ошибки ({len(errors)}):")
            for error in errors[:5]:  # Показываем первые 5 ошибок
                print(f"   • {error}")
        
        return imported_books
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return []

def get_fantasy_category_url():
    """Получает URL категории фэнтези"""
    try:
        client = FlibustaTorClient(use_tor=True)
        
        # Получаем категории
        print("🔍 Ищем категории...")
        categories = client.browse_categories()
        
        if not categories:
            print("❌ Категории не найдены")
            return None
        
        # Ищем категорию "По жанрам"
        genres_category = None
        for category in categories:
            if any(keyword in category['name'].lower() for keyword in ['жанр', 'genre']):
                genres_category = category
                print(f"📂 Найдена категория жанров: {category['name']}")
                break
        
        if not genres_category:
            print("❌ Категория жанров не найдена")
            return None
        
        # Получаем жанры
        print(f"🔍 Ищем фэнтези в категории: {genres_category['name']}")
        genre_items = client._get_categories_from_catalog(genres_category['url'], limit=100)
        
        # Ищем фэнтези среди жанров
        fantasy_genre = None
        for item in genre_items:
            title = item.get('title', '').lower()
            if any(keyword in title for keyword in ['фэнтези', 'fantasy', 'фантаст']):
                fantasy_genre = item
                print(f"🎯 Найден жанр фэнтези: {item.get('title')}")
                break
        
        if not fantasy_genre:
            print("❌ Жанр фэнтези не найден")
            # Попробуем взять первый доступный жанр
            if genre_items:
                fantasy_genre = genre_items[0]
                print(f"⚠️  Используем первый доступный жанр: {fantasy_genre.get('title')}")
            else:
                return None
        
        # Возвращаем URL жанра
        genre_url = fantasy_genre.get('download_url') or fantasy_genre.get('url', '')
        return genre_url
        
    except Exception as e:
        print(f"❌ Ошибка поиска категории: {e}")
        return None

if __name__ == '__main__':
    print("=== Импорт книг по категории ===\n")
    
    # Проверяем подключение к базе данных
    try:
        book_count = Book.objects.count()
        print(f"📊 Текущее количество книг в БД: {book_count}")
        print()
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        sys.exit(1)
    
    # Получаем URL категории фэнтези
    category_url = get_fantasy_category_url()
    
    if not category_url:
        print("❌ Не удалось найти подходящую категорию")
        sys.exit(1)
    
    print(f"🔗 URL категории: {category_url}\n")
    
    # Импортируем 5 книг
    imported_books = import_books_by_category(category_url, count=5)
    
    print(f"\n🎉 Готово! Импортировано {len(imported_books)} книг")