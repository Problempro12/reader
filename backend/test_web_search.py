#!/usr/bin/env python
"""
Тест веб-поиска Flibusta для получения ссылок на скачивание
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient
from books.models import Book, Author
from users.models import User

def test_web_search():
    """Тест веб-поиска Flibusta"""
    
    print("=== Тест веб-поиска Flibusta ===")
    
    # Создаем клиент
    client = FlibustaTorClient(use_tor=False)
    
    # Тестируем разные методы поиска
    query = "Пушкин"
    print(f"\n🔍 Поиск по запросу: {query}")
    
    # 1. OPDS поиск
    print("\n1. OPDS поиск:")
    try:
        opds_results = client._search_via_opds(query, limit=3)
        print(f"   Найдено: {len(opds_results)} книг")
        for i, book in enumerate(opds_results):
            print(f"   📚 {i+1}. {book.get('title')} - {book.get('author')}")
            print(f"      Ссылки: {len(book.get('download_links', []))}")
            for link in book.get('download_links', []):
                print(f"        - {link.get('format')}: {link.get('url')}")
    except Exception as e:
        print(f"   ❌ Ошибка OPDS: {e}")
    
    # 2. Веб-поиск
    print("\n2. Веб-поиск:")
    try:
        web_results = client._search_via_web(query, limit=3)
        print(f"   Найдено: {len(web_results)} книг")
        for i, book in enumerate(web_results):
            print(f"   📚 {i+1}. {book.get('title')} - {book.get('author')}")
            print(f"      Ссылки: {len(book.get('download_links', []))}")
            print(f"      Source ID: {book.get('source_id')}")
            for link in book.get('download_links', []):
                print(f"        - {link.get('format')}: {link.get('url')}")
    except Exception as e:
        print(f"   ❌ Ошибка веб-поиска: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Общий метод search_books
    print("\n3. Общий метод search_books:")
    try:
        all_results = client.search_books(query, limit=3)
        print(f"   Найдено: {len(all_results)} книг")
        for i, book in enumerate(all_results):
            print(f"   📚 {i+1}. {book.get('title')} - {book.get('author')}")
            print(f"      Ссылки: {len(book.get('download_links', []))}")
            print(f"      Source ID: {book.get('source_id')}")
            for link in book.get('download_links', []):
                print(f"        - {link.get('format')}: {link.get('url')}")
                
        # Попробуем загрузить первую книгу с ссылками
        books_with_links = [book for book in all_results if book.get('download_links')]
        if books_with_links:
            first_book = books_with_links[0]
            print(f"\n4. Попытка загрузки: {first_book.get('title')}")
            
            try:
                from books.external_sources import import_book_from_external_source
                content = import_book_from_external_source(
                    book_data=first_book,
                    source='flibusta',
                    download_format='fb2',
                    use_tor=True
                )
                
                if content:
                    print(f"   ✅ Книга загружена! Размер: {len(content)} символов")
                    print(f"   Первые 200 символов: {content[:200]}...")
                    
                    # Попробуем сохранить в БД
                    try:
                        author_name = first_book.get('author', 'Неизвестный автор')
                        author, created = Author.objects.get_or_create(
                            name=author_name,
                            defaults={'bio': 'Автор импортирован из Flibusta'}
                        )
                        
                        # Проверяем, нет ли уже такой книги
                        existing_book = Book.objects.filter(
                            title=first_book.get('title'),
                            author=author
                        ).first()
                        
                        if existing_book:
                            print(f"   📖 Книга уже существует в БД: ID {existing_book.id}")
                        else:
                            new_book = Book.objects.create(
                                title=first_book.get('title'),
                                author=author,
                                content=content,
                                description=first_book.get('description', ''),
                                source='flibusta',
                                source_id=first_book.get('source_id')
                            )
                            print(f"   ✅ Книга сохранена в БД: ID {new_book.id}")
                            
                    except Exception as e:
                        print(f"   ❌ Ошибка сохранения в БД: {e}")
                        
                else:
                    print(f"   ❌ Не удалось загрузить содержимое")
                    
            except Exception as e:
                print(f"   ❌ Ошибка загрузки: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ❌ Нет книг с ссылками для загрузки")
            
    except Exception as e:
        print(f"   ❌ Ошибка общего поиска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Запуск теста веб-поиска Flibusta\n")
    
    # Проверяем подключение к БД
    try:
        book_count = Book.objects.count()
        author_count = Author.objects.count()
        user_count = User.objects.count()
        print(f"📊 Статистика БД:")
        print(f"   Книги: {book_count}")
        print(f"   Авторы: {author_count}")
        print(f"   Пользователи: {user_count}")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        sys.exit(1)
    
    # Запускаем тесты
    test_web_search()
    
    print("\n✅ Тесты завершены!")