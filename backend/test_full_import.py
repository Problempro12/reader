#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
import django
django.setup()

from books.models import Book, Author
from books.external_sources import import_book_from_external_source, search_external_books
import logging
from datetime import datetime

def save_book_to_database(book_data, content):
    """Сохранение книги в базу данных"""
    try:
        # Получаем или создаем автора
        author_name = book_data.get('author', 'Неизвестный автор')
        author, created = Author.objects.get_or_create(
            name=author_name,
            defaults={'bio': f'Автор книги "{book_data.get("title", "")}"'}
        )
        
        # Создаем книгу
        book = Book.objects.create(
            title=book_data.get('title', 'Неизвестное название'),
            author=author,
            content=content,
            description=book_data.get('description', ''),
            genre=book_data.get('genre', ''),
            published_date=datetime.now().date(),
            vote_count=0
        )
        
        return {'success': True, 'book_id': book.id, 'book': book}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_full_import():
    """Тест полноценного импорта книги в базу данных"""
    print("=== Тест полноценного импорта книги ===")
    
    # Поиск и импорт книги
    query = "Пушкин"
    print(f"\nПоиск книги: {query}")
    
    try:
        # Сначала ищем книги
        search_results = search_external_books(query, sources=['flibusta'], use_tor=True, limit=3)
        
        if search_results['flibusta']:
            print(f"✓ Найдено {len(search_results['flibusta'])} книг")
            
            # Берем первую книгу для импорта
            book_data = search_results['flibusta'][0]
            print(f"Импортируем: {book_data.get('title', 'Неизвестное название')} - {book_data.get('author', 'Неизвестный автор')}")
            
            # Скачиваем содержимое книги
            content = import_book_from_external_source(
                book_data=book_data,
                source='flibusta',
                download_format='fb2',
                use_tor=True
            )
            
            if content:
                print(f"✓ Книга успешно скачана")
                print(f"Содержимое: {len(content)} символов")
                print(f"Начало содержимого: {content[:200]}...")
                
                # Сохраняем книгу в базу данных
                save_result = save_book_to_database(book_data, content)
                
                if save_result['success']:
                    book = save_result['book']
                    book_id = save_result['book_id']
                    print(f"✓ Книга сохранена в базу данных с ID: {book_id}")
                    
                    print(f"\n=== Информация о книге ===")
                    print(f"Название: {book.title}")
                    print(f"Автор: {book.author.name}")
                    print(f"Описание: {book.description[:200] if book.description else 'Нет описания'}...")
                    print(f"Жанр: {book.genre}")
                    print(f"Дата публикации: {book.published_date}")
                    print(f"Голосов: {book.vote_count}")
                    print(f"Создана: {book.created_at}")
                    
                    # Проверяем содержимое
                    if book.content:
                        print(f"\n=== Содержимое книги ===")
                        print(f"Размер содержимого: {len(book.content)} символов")
                        
                        # Показываем начало содержимого
                        preview = book.content[:500] if len(book.content) > 500 else book.content
                        print(f"\nНачало содержимого:")
                        print("-" * 50)
                        print(preview)
                        print("-" * 50)
                        
                        # Проверяем формат
                        if book.content.strip().startswith('<?xml') and 'FictionBook' in book.content:
                            print("✓ Содержимое в формате FB2")
                        elif book.content.strip().startswith('<'):
                            print("⚠ Содержимое в XML формате, но возможно не FB2")
                        else:
                            print("⚠ Содержимое не в XML формате")
                    else:
                        print("✗ Содержимое книги отсутствует")
                        
                    print(f"\n✓ Книга полностью импортирована и доступна в базе данных")
                    print(f"URL для чтения: http://localhost:8000/books/{book_id}/read")
                else:
                    print(f"✗ Ошибка сохранения в базу данных: {save_result['error']}")
            else:
                print("✗ Не удалось скачать книгу")
        else:
            print("✗ Книги не найдены")
            
    except Exception as e:
        print(f"✗ Исключение при импорте: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_import():
    """Тест импорта нескольких книг"""
    print("\n\n=== Тест импорта нескольких книг ===")
    
    queries = ["Чехов", "Гоголь", "Лермонтов"]
    
    for query in queries:
        print(f"\n--- Импорт книги: {query} ---")
        
        try:
            # Сначала ищем книги
            search_results = search_external_books(query, sources=['flibusta'], use_tor=True, limit=1)
            
            if search_results['flibusta']:
                book_data = search_results['flibusta'][0]
                
                content = import_book_from_external_source(
                    book_data=book_data,
                    source='flibusta',
                    download_format='fb2',
                    use_tor=True
                )
                
                if content:
                    save_result = save_book_to_database(book_data, content)
                    
                    if save_result['success']:
                        book = save_result['book']
                        book_id = save_result['book_id']
                        print(f"✓ Импортирована: '{book.title}' (ID: {book_id})")
                    else:
                        print(f"✗ Ошибка сохранения: {save_result['error']}")
                else:
                    print(f"✗ Ошибка скачивания книги")
            else:
                print(f"✗ Книги не найдены для запроса: {query}")
                
        except Exception as e:
            print(f"✗ Исключение: {e}")
    
    # Показываем общую статистику
    total_books = Book.objects.count()
    
    print(f"\n=== Статистика ===")
    print(f"Всего книг в базе: {total_books}")
    
    # Показываем последние добавленные книги
    recent_books = Book.objects.order_by('-created_at')[:5]
    print(f"\nПоследние добавленные книги:")
    for book in recent_books:
        print(f"  - {book.title} ({book.author.name}) - {book.created_at.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    test_full_import()
    test_multiple_import()