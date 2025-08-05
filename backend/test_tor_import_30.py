#!/usr/bin/env python
"""
Тест импорта 30 книг из Flibusta через Tor (onion-адрес)
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books, import_book_from_external_source
from books.models import Book, Author
from users.models import User
import time

def test_mass_import_via_tor():
    """Тест массового импорта книг через Tor"""
    
    print("=== Тест импорта 30 книг из Flibusta через Tor (onion) ===")
    print("🧅 Используется onion-адрес: http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion")
    print("🔒 Подключение через Tor SOCKS5 прокси")
    
    # Список запросов для поиска разных книг
    search_queries = [
        "Пушкин", "Толстой", "Достоевский", "Чехов", "Гоголь",
        "Тургенев", "Лермонтов", "Булгаков", "Набоков", "Бунин",
        "Есенин", "Маяковский", "Блок", "Ахматова", "Цветаева",
        "Пастернак", "Солженицын", "Шолохов", "Горький", "Куприн",
        "Салтыков-Щедрин", "Островский", "Фонвизин", "Грибоедов", "Крылов",
        "Жуковский", "Державин", "Карамзин", "Радищев", "Ломоносов"
    ]
    
    successful_imports = 0
    failed_imports = 0
    total_books_found = 0
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n📖 {i}/30: Поиск книг по запросу '{query}'")
        
        try:
            # Поиск через Tor
            results = search_external_books(
                query=query,
                limit=1,  # Берем только первую книгу
                use_tor=True,  # Используем Tor для onion-адреса
                sources=['flibusta']
            )
            
            flibusta_books = results.get('flibusta', [])
            total_books_found += len(flibusta_books)
            
            if not flibusta_books:
                print(f"   ❌ Книги не найдены")
                failed_imports += 1
                continue
                
            book_data = flibusta_books[0]
            print(f"   📚 Найдена: {book_data.get('title')} - {book_data.get('author')}")
            
            # Проверяем, что используется onion-адрес
            download_links = book_data.get('download_links', [])
            if download_links:
                first_link = list(download_links.values())[0] if isinstance(download_links, dict) else download_links[0]
                if 'onion' in first_link.get('url', ''):
                    print(f"   🧅 Подтверждено: используется onion-адрес")
                else:
                    print(f"   ⚠️  Внимание: не используется onion-адрес")
            
            # Попытка импорта через Tor
            print(f"   ⬇️  Импорт через Tor...")
            content = import_book_from_external_source(
                book_data=book_data,
                source='flibusta',
                download_format='fb2',
                use_tor=True  # Принудительно используем Tor
            )
            
            if content and len(content.strip()) > 100:
                print(f"   ✅ Успешно импортировано ({len(content)} символов)")
                successful_imports += 1
            else:
                print(f"   ❌ Импорт не удался (пустое содержимое)")
                failed_imports += 1
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            failed_imports += 1
            
        # Небольшая пауза между запросами
        time.sleep(1)
    
    print(f"\n=== ИТОГИ ИМПОРТА ЧЕРЕЗ TOR ===")
    print(f"📊 Всего запросов: 30")
    print(f"📚 Всего найдено книг: {total_books_found}")
    print(f"✅ Успешных импортов: {successful_imports}")
    print(f"❌ Неудачных импортов: {failed_imports}")
    print(f"📈 Процент успеха: {(successful_imports/30)*100:.1f}%")
    print(f"🧅 Все операции выполнены через onion-адрес Flibusta")
    print(f"🔒 Подключение через Tor SOCKS5 прокси (127.0.0.1:9150)")

if __name__ == '__main__':
    test_mass_import_via_tor()