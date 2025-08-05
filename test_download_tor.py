#!/usr/bin/env python3
"""
Тестирование загрузки книг из Flibusta через Tor (onion-адрес)
"""

import sys
import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
django.setup()

from books.external_sources import search_external_books, import_book_from_external_source
from books.models import Book, Author

def test_download_books():
    """Тестирование загрузки книг через Tor"""
    print("=== Тестирование загрузки книг из Flibusta через Tor ===")
    
    # 1. Поиск книг через Tor
    print("\n1. Поиск книг через Tor (onion-адрес):")
    try:
        results = search_external_books("Пушкин", use_tor=True, limit=3)
        
        if results and results.get('flibusta'):
            flibusta_books = results['flibusta']
            print(f"✅ Найдено {len(flibusta_books)} книг через Tor")
            
            # Берем первую книгу для загрузки
            first_book = flibusta_books[0] if flibusta_books else None
            
            if first_book and isinstance(first_book, dict):
                print(f"\n📚 Выбрана книга для загрузки:")
                print(f"   Название: {first_book.get('title', 'Без названия')}")
                print(f"   Автор: {first_book.get('author', 'Неизвестный автор')}")
                print(f"   Source ID: {first_book.get('source_id', 'Нет ID')}")
                print(f"   Ссылки для скачивания: {len(first_book.get('download_links', []))}")
                
                # Показываем доступные форматы
                for link in first_book.get('download_links', []):
                    print(f"     - {link.get('format', 'unknown')}: {link.get('url', 'no url')}")
                
                # 2. Попытка загрузки книги
                # Определяем лучший доступный формат для чтения
                available_formats = [link.get('format') for link in first_book.get('download_links', [])]
                
                # Приоритет форматов для чтения: fb2 > epub > txt
                preferred_formats = ['fb2', 'epub', 'txt']
                download_format = None
                
                for fmt in preferred_formats:
                    if fmt in available_formats:
                        download_format = fmt
                        break
                
                # Если ни один из предпочитаемых форматов не найден, берем первый доступный
                if not download_format and available_formats:
                    download_format = available_formats[0]
                elif not download_format:
                    download_format = 'fb2'  # fallback
                
                print(f"\n2. Загрузка книги в формате {download_format.upper()}:")
                print(f"   Доступные форматы: {', '.join(available_formats)}")
                try:
                    content = import_book_from_external_source(
                        source='flibusta',
                        book_data=first_book,
                        download_format=download_format
                    )
                    
                    if content:
                        print(f"✅ Книга успешно загружена!")
                        print(f"   Размер содержимого: {len(content)} символов")
                        print(f"   Первые 300 символов: {content[:300]}...")
                        
                        # 3. Сохранение в базу данных
                        print(f"\n3. Сохранение в базу данных:")
                        try:
                            # Создаем или получаем автора
                            author_name = first_book.get('author', 'Неизвестный автор')
                            author, created = Author.objects.get_or_create(
                                name=author_name,
                                defaults={'bio': f'Автор импортирован из Flibusta через Tor'}
                            )
                            print(f"   Автор: {author.name} (создан: {created})")
                            
                            # Проверяем, нет ли уже такой книги
                            book_title = first_book.get('title', 'Без названия')
                            existing_book = Book.objects.filter(
                                title=book_title,
                                author=author
                            ).first()
                            
                            if existing_book:
                                print(f"   📖 Книга уже существует в БД: ID {existing_book.id}")
                                print(f"   Обновляем содержимое и жанр...")
                                existing_book.content = content
                                existing_book.genre = first_book.get('genre', '')
                                existing_book.save()
                                print(f"   ✅ Содержимое и жанр обновлены")
                            else:
                                new_book = Book.objects.create(
                                    title=book_title,
                                    author=author,
                                    content=content,
                                    description=first_book.get('description', 'Книга загружена из Flibusta через Tor'),
                                    genre=first_book.get('genre', '')
                                )
                                print(f"   ✅ Новая книга создана в БД: ID {new_book.id}")
                                
                        except Exception as e:
                            print(f"   ❌ Ошибка сохранения в БД: {e}")
                            
                    else:
                        print(f"❌ Не удалось загрузить содержимое книги")
                        
                except Exception as e:
                    print(f"❌ Ошибка загрузки книги: {e}")
                    
            else:
                print("❌ Не удалось получить данные первой книги")
                
        else:
            print("❌ Книги не найдены через Tor")
            
    except Exception as e:
        print(f"❌ Ошибка поиска через Tor: {e}")
    
    # 4. Статистика БД
    print(f"\n4. Статистика базы данных:")
    try:
        book_count = Book.objects.count()
        author_count = Author.objects.count()
        print(f"   📚 Всего книг: {book_count}")
        print(f"   👤 Всего авторов: {author_count}")
        
        # Показываем последние добавленные книги
        recent_books = Book.objects.order_by('-id')[:3]
        print(f"   📖 Последние книги:")
        for book in recent_books:
            print(f"     - {book.title} ({book.author.name}) - ID: {book.id}")
            
    except Exception as e:
        print(f"   ❌ Ошибка получения статистики: {e}")
    
    print("\n=== Тестирование завершено ===")

if __name__ == "__main__":
    test_download_books()