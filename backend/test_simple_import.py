#!/usr/bin/env python
"""
Простой тест импорта одной книги из Flibusta
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books, import_book_from_external_source
from books.models import Book, Author
from books.views import import_external_book_view
from users.models import User
from django.test import RequestFactory
from django.http import JsonResponse
import json

def test_search_and_import():
    """Тест поиска и импорта книги"""
    
    print("=== Тест поиска и импорта книги из Flibusta ===")
    
    # 1. Поиск книг
    query = "Пушкин"
    print(f"\n1. Поиск книг по запросу: {query}")
    
    try:
        results = search_external_books(
            query=query,
            limit=5,
            use_tor=True,
            sources=['flibusta']
        )
        
        flibusta_books = results.get('flibusta', [])
        print(f"Найдено книг: {len(flibusta_books)}")
        
        if not flibusta_books:
            print("❌ Книги не найдены")
            return
        
        # Выводим найденные книги
        for i, book in enumerate(flibusta_books):
            print(f"\n📚 Книга {i+1}:")
            print(f"  Название: {book.get('title')}")
            print(f"  Автор: {book.get('author')}")
            print(f"  Описание: {book.get('description', '')[:100]}...")
            print(f"  Ссылки для скачивания: {len(book.get('download_links', []))}")
            print(f"  Source ID: {book.get('source_id')}")
            
            # Показываем ссылки, если есть
            for link in book.get('download_links', []):
                print(f"    - {link.get('format')}: {link.get('url')}")
        
        # 2. Попытка импорта первой книги
        first_book = flibusta_books[0]
        print(f"\n2. Попытка импорта книги: {first_book.get('title')}")
        
        try:
            content = import_book_from_external_source(
                book_data=first_book,
                source='flibusta',
                download_format='fb2',
                use_tor=True
            )
            
            if content:
                print(f"✅ Книга успешно загружена!")
                print(f"   Размер содержимого: {len(content)} символов")
                print(f"   Первые 200 символов: {content[:200]}...")
                
                # 3. Попытка создания книги в БД
                print(f"\n3. Создание книги в БД")
                
                try:
                    # Создаем или получаем автора
                    author_name = first_book.get('author', 'Неизвестный автор')
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={'bio': 'Автор импортирован из Flibusta'}
                    )
                    print(f"   Автор: {author.name} (создан: {created})")
                    
                    # Проверяем, нет ли уже такой книги
                    existing_book = Book.objects.filter(
                        title=first_book.get('title'),
                        author=author
                    ).first()
                    
                    if existing_book:
                        print(f"📖 Книга уже существует в БД: ID {existing_book.id}")
                    else:
                        # Создаем новую книгу
                        new_book = Book.objects.create(
                            title=first_book.get('title'),
                            author=author,
                            content=content,
                            description=first_book.get('description', ''),
                            source='flibusta',
                            source_id=first_book.get('source_id')
                        )
                        print(f"✅ Книга создана в БД: ID {new_book.id}")
                        
                        # Проверяем, что книга действительно создалась
                        saved_book = Book.objects.get(id=new_book.id)
                        print(f"   Проверка: {saved_book.title} by {saved_book.author.name}")
                        print(f"   Размер содержимого в БД: {len(saved_book.content)} символов")
                    
                except Exception as e:
                    print(f"❌ Ошибка при работе с БД: {e}")
                    
            else:
                print(f"❌ Не удалось загрузить содержимое книги")
                print(f"   Возможные причины:")
                print(f"   - Нет ссылок для скачивания")
                print(f"   - Ссылки недоступны")
                print(f"   - Проблемы с форматом файла")
                
        except Exception as e:
            print(f"❌ Ошибка импорта: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Запуск простого теста импорта из Flibusta\n")
    
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
    test_search_and_import()
    
    print("\n✅ Тесты завершены!")