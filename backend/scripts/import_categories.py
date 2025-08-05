#!/usr/bin/env python
"""
Тест импорта книг по категориям из Флибусты с сортировкой по популярности
"""

import os
import sys
import django
import requests
import time

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book, Author
from books.external_sources import FlibustaTorClient

def test_browse_categories():
    """Тест получения списка категорий"""
    print("=== Тест получения категорий ===\n")
    
    try:
        # Создаем клиент с Tor для подключения к onion-адресу
        client = FlibustaTorClient(use_tor=True)
        
        print(f"🔗 Подключение к: {client.opds_url}")
        
        # Получаем категории
        categories = client.browse_categories()
        
        print(f"📂 Найдено категорий: {len(categories)}\n")
        
        for i, category in enumerate(categories[:10]):  # Показываем первые 10
            print(f"{i+1:2d}. {category['name']}")
            print(f"    URL: {category['url']}\n")
        
        if len(categories) > 10:
            print(f"... и еще {len(categories) - 10} категорий\n")
        
        return categories
        
    except Exception as e:
        print(f"❌ Ошибка получения категорий: {e}")
        return []

def test_browse_category_books(category_url: str, category_name: str):
    """Тест получения книг из категории"""
    print(f"=== Тест получения книг из категории: {category_name} ===\n")
    
    try:
        # Создаем клиент без Tor для тестирования
        client = FlibustaTorClient(use_tor=False)
        
        print(f"🔗 Запрос к: {category_url}")
        
        # Получаем книги с сортировкой по популярности
        books = client.browse_books_by_category(category_url, sort_by_popularity=True, limit=10)
        
        print(f"📚 Найдено книг: {len(books)}\n")
        
        for i, book in enumerate(books):
            print(f"{i+1:2d}. {book.get('title', 'Без названия')}")
            print(f"    Автор: {book.get('author', 'Неизвестен')}")
            print(f"    Описание: {book.get('description', 'Нет описания')[:100]}...")
            print(f"    Ссылки для скачивания: {len(book.get('download_links', []))}")
            
            # Показываем доступные форматы
            formats = [link.get('format', 'unknown') for link in book.get('download_links', [])]
            if formats:
                print(f"    Форматы: {', '.join(formats)}")
            print()
        
        return books
        
    except Exception as e:
        print(f"❌ Ошибка получения книг из категории: {e}")
        return []

def test_api_endpoints():
    """Тест API эндпоинтов"""
    print("=== Тест API эндпоинтов ===\n")
    
    base_url = "http://localhost:8000"
    
    # Тест получения категорий
    print("1. Тест /api/books/browse_categories/")
    try:
        response = requests.get(f"{base_url}/api/books/browse_categories/?use_tor=true", timeout=30)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Найдено категорий: {data.get('total_found', 0)}")
            
            categories = data.get('categories', [])
            if categories:
                print(f"   Первая категория: {categories[0].get('name')}")
                
                # Тест получения книг из первой категории
                print("\n2. Тест /api/books/browse_category_books/")
                category_url = categories[0].get('url')
                
                response2 = requests.get(
                    f"{base_url}/api/books/browse_category_books/",
                    params={
                        'category_url': category_url,
                        'use_tor': 'true',
                        'sort_by_popularity': 'true',
                        'limit': '5'
                    },
                    timeout=30
                )
                
                print(f"   Статус: {response2.status_code}")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    print(f"   Найдено книг: {data2.get('total_found', 0)}")
                    print(f"   Сортировка по популярности: {data2.get('sorted_by_popularity', False)}")
                    
                    books = data2.get('books', [])
                    if books:
                        print(f"   Первая книга: {books[0].get('title')} - {books[0].get('author')}")
                else:
                    print(f"   Ошибка: {response2.text}")
            
        else:
            print(f"   Ошибка: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка API: {e}")

def test_mass_import_simulation():
    """Симуляция массового импорта книг фэнтези из категории жанров"""
    print("=== Симуляция массового импорта книг фэнтези ===\n")
    
    try:
        # Получаем категории
        client = FlibustaTorClient(use_tor=True)
        categories = client.browse_categories()
        
        if not categories:
            print("❌ Нет доступных категорий для импорта")
            return
        
        # Ищем категорию "По жанрам"
        genres_category = None
        for category in categories:
            if any(keyword in category['name'].lower() for keyword in ['жанр', 'genre']):
                genres_category = category
                print(f"📂 Найдена категория жанров: {category['name']}")
                break
        
        if not genres_category:
            print("❌ Категория жанров не найдена")
            return
        
        # Получаем содержимое категории жанров
        print(f"🔍 Ищем фэнтези в категории: {genres_category['name']}")
        print(f"🔗 URL категории: {genres_category['url']}")
        
        # Используем специальный метод для получения категорий/жанров
        genre_items = client._get_categories_from_catalog(genres_category['url'], limit=100)
        
        print(f"📋 Найдено элементов в категории: {len(genre_items)}")
        
        # Показываем первые несколько элементов для отладки
        if genre_items:
            print("📝 Первые элементы в категории:")
            for i, item in enumerate(genre_items[:5]):
                print(f"   {i+1}. {item.get('title', 'Без названия')} (тип: {type(item).__name__})")
        
        # Ищем фэнтези среди жанров
        fantasy_genre = None
        for item in genre_items:
            title = item.get('title', '').lower()
            if any(keyword in title for keyword in ['фэнтези', 'fantasy', 'фантаст']):
                fantasy_genre = item
                print(f"🎯 Найден жанр фэнтези: {item.get('title')}")
                break
        
        if not fantasy_genre:
            print("❌ Жанр фэнтези не найден в категории жанров")
            # Попробуем взять первый доступный жанр для демонстрации
            if genre_items:
                fantasy_genre = genre_items[0]
                print(f"⚠️  Используем первый доступный жанр: {fantasy_genre.get('title')}")
            else:
                print("❌ Нет доступных жанров")
                return
        
        # Получаем книги из жанра фэнтези
        print(f"📚 Получаем книги из жанра: {fantasy_genre.get('title')}")
        
        # Если у элемента есть download_url, используем его как URL для получения книг
        genre_url = fantasy_genre.get('download_url') or fantasy_genre.get('url', '')
        if not genre_url:
            print("❌ Не найден URL для жанра")
            return
        
        books = client.browse_books_by_category(genre_url, sort_by_popularity=True, limit=5)
        
        print(f"📚 Найдено книг для импорта: {len(books)}\n")
        
        # Симулируем процесс импорта
        for i, book in enumerate(books):
            print(f"📖 {i+1}. Импорт: {book.get('title')} - {book.get('author')}")
            
            # Проверяем, есть ли уже такая книга
            existing = Book.objects.filter(
                title=book.get('title', ''),
                author__name=book.get('author', '')
            ).first()
            
            if existing:
                print(f"   ⚠️  Книга уже существует в БД (ID: {existing.id})")
            else:
                print(f"   ✅ Книга готова к импорту")
                print(f"   📋 Форматы: {[link.get('format') for link in book.get('download_links', [])]}")
            
            print()
        
        print("💡 Для реального импорта используйте API эндпоинт /api/books/import_category_books/")
        
    except Exception as e:
        print(f"❌ Ошибка симуляции импорта: {e}")

def main():
    print("🚀 Тестирование импорта книг по категориям из Флибусты\n")
    
    # Проверяем подключение к БД
    try:
        book_count = Book.objects.count()
        author_count = Author.objects.count()
        print(f"📊 Текущее состояние БД:")
        print(f"   Книг: {book_count}")
        print(f"   Авторов: {author_count}\n")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return
    
    # Запускаем тесты
    print("🔍 Начинаем тестирование...\n")
    
    # 1. Тест получения категорий
    categories = test_browse_categories()
    
    if categories:
        # 2. Тест получения книг из первой категории
        first_category = categories[0]
        test_browse_category_books(first_category['url'], first_category['name'])
    
    # 3. Тест API эндпоинтов
    test_api_endpoints()
    
    # 4. Симуляция массового импорта
    test_mass_import_simulation()
    
    print("\n✅ Тестирование завершено!")
    print("\n📝 Доступные API эндпоинты:")
    print("   GET  /api/books/browse_categories/ - получить список категорий")
    print("   GET  /api/books/browse_category_books/ - получить книги из категории")
    print("   POST /api/books/import_category_books/ - массовый импорт книг из категории")

if __name__ == '__main__':
    main()