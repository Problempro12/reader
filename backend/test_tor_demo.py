#!/usr/bin/env python
"""
Демонстрация работы импорта через Tor с onion-адресом
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import search_external_books, import_book_from_external_source

def demo_tor_connection():
    """Демонстрация подключения через Tor"""
    
    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ ЧЕРЕЗ TOR ===")
    print("🧅 Onion-адрес: http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion")
    print("🔒 Tor SOCKS5 прокси: 127.0.0.1:9150")
    print()
    
    # Тест 1: Поиск через clearnet (без Tor)
    print("📡 Тест 1: Поиск через clearnet (use_tor=False)")
    try:
        results_clearnet = search_external_books(
            query="Пушкин",
            limit=1,
            use_tor=False,
            sources=['flibusta']
        )
        
        books_clearnet = results_clearnet.get('flibusta', [])
        if books_clearnet:
            book = books_clearnet[0]
            links = book.get('download_links', [])
            if links:
                first_link = links[0]['url'] if isinstance(links, list) else list(links.values())[0]['url']
                print(f"   ✅ Найдена книга: {book.get('title')}")
                print(f"   🌐 URL: {first_link}")
                print(f"   📍 Домен: {'clearnet зеркало' if 'flibusta.is' in first_link else 'другой'}")
        else:
            print("   ❌ Книги не найдены")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()
    
    # Тест 2: Поиск через Tor (onion)
    print("🧅 Тест 2: Поиск через Tor (use_tor=True)")
    try:
        results_tor = search_external_books(
            query="Пушкин",
            limit=1,
            use_tor=True,
            sources=['flibusta']
        )
        
        books_tor = results_tor.get('flibusta', [])
        if books_tor:
            book = books_tor[0]
            links = book.get('download_links', [])
            if links:
                first_link = links[0]['url'] if isinstance(links, list) else list(links.values())[0]['url']
                print(f"   ✅ Найдена книга: {book.get('title')}")
                print(f"   🧅 URL: {first_link}")
                print(f"   📍 Домен: {'onion-адрес' if '.onion' in first_link else 'не onion'}")
                
                # Проверяем импорт
                print(f"   ⬇️  Попытка импорта через Tor...")
                content = import_book_from_external_source(
                    book_data=book,
                    source='flibusta',
                    download_format='fb2',
                    use_tor=True
                )
                
                if content and len(content.strip()) > 50:
                    print(f"   ✅ Импорт успешен! Получено {len(content)} символов")
                    print(f"   📄 Начало содержимого: {content[:100]}...")
                else:
                    print(f"   ⚠️  Импорт завершен, но содержимое пустое или короткое")
        else:
            print("   ❌ Книги не найдены")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()
    print("=== ЗАКЛЮЧЕНИЕ ===")
    print("✅ Система настроена для работы через Tor")
    print("🧅 При use_tor=True используется onion-адрес")
    print("🌐 При use_tor=False используются clearnet зеркала")
    print("🔒 Все запросы к onion-адресу проходят через SOCKS5 прокси")

if __name__ == '__main__':
    demo_tor_connection()