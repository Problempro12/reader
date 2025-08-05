#!/usr/bin/env python
"""
Тест импорта книги из Flibusta с детальной диагностикой
"""

import os
import sys
import django
import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient, search_external_books, import_book_from_external_source
from books.models import Book, Author
from django.contrib.auth.models import User

def test_flibusta_direct():
    """Прямое тестирование FlibustaTorClient"""
    
    print("=== Прямой тест FlibustaTorClient ===")
    
    # Создаем клиент без Tor для тестирования
    client = FlibustaTorClient(use_tor=False)
    
    query = "Пушкин"
    print(f"Поиск книг по запросу: {query}")
    print(f"OPDS URL: {client.opds_url}")
    print(f"Base URL: {client.base_url}")
    
    # Тестируем прямой запрос к OPDS
    search_url = f"{client.opds_url}/search?searchTerm={query}"
    print(f"\nЗапрос к: {search_url}")
    
    try:
        response = client.session.get(search_url, timeout=client.timeout)
        print(f"Статус ответа: {response.status_code}")
        print(f"Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            # Показываем первые 1000 символов ответа
            content_preview = response.text[:1000]
            print(f"\nПервые 1000 символов ответа:")
            print(content_preview)
            print("...")
            
            # Пробуем парсить XML
            try:
                root = ET.fromstring(response.content)
                print(f"\nXML успешно распарсен. Корневой элемент: {root.tag}")
                
                # Namespace для OPDS
                ns = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'opds': 'http://opds-spec.org/2010/catalog'
                }
                
                entries = root.findall('.//atom:entry', ns)
                print(f"Найдено записей: {len(entries)}")
                
                for i, entry in enumerate(entries[:3]):
                    print(f"\n--- Запись {i+1} ---")
                    
                    title = entry.find('atom:title', ns)
                    author = entry.find('atom:author/atom:name', ns)
                    summary = entry.find('atom:summary', ns)
                    
                    print(f"Название: {title.text if title is not None else 'Не найдено'}")
                    print(f"Автор: {author.text if author is not None else 'Не найдено'}")
                    print(f"Описание: {summary.text[:100] if summary is not None else 'Не найдено'}...")
                    
                    # Ищем ссылки
                    links = entry.findall('atom:link', ns)
                    download_links = []
                    for link in links:
                        rel = link.get('rel')
                        if rel == 'http://opds-spec.org/acquisition':
                            download_links.append({
                                'href': link.get('href'),
                                'type': link.get('type'),
                                'rel': rel
                            })
                    
                    print(f"Ссылки для скачивания: {len(download_links)}")
                    for link in download_links:
                        print(f"  - {link['type']}: {link['href']}")
                        
            except ET.ParseError as e:
                print(f"❌ Ошибка парсинга XML: {e}")
                
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            print(f"Ответ: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тестируем метод search_books
    print(f"\n=== Тест метода search_books ===")
    try:
        books = client.search_books(query, limit=3)
        print(f"Найдено книг: {len(books)}")
        
        for i, book in enumerate(books):
            print(f"\n📚 Книга {i+1}:")
            print(f"  Название: {book.get('title')}")
            print(f"  Автор: {book.get('author')}")
            print(f"  Описание: {book.get('description', '')[:100]}...")
            print(f"  Ссылки: {len(book.get('download_links', []))}")
            for link in book.get('download_links', []):
                print(f"    - {link.get('format')}: {link.get('url')}")
                
    except Exception as e:
        print(f"❌ Ошибка search_books: {e}")

def test_alternative_search():
    """Тест альтернативных способов поиска"""
    
    print("\n=== Тест альтернативных способов поиска ===")
    
    # Пробуем разные запросы
    queries = ["Пушкин", "Толстой", "Война и мир", "Евгений Онегин"]
    
    for query in queries:
        print(f"\nПоиск: {query}")
        try:
            results = search_external_books(
                query=query,
                limit=2,
                use_tor=False,
                sources=['flibusta']
            )
            
            flibusta_results = results.get('flibusta', [])
            print(f"Результатов: {len(flibusta_results)}")
            
            for book in flibusta_results:
                print(f"  - {book.get('title')} ({book.get('author')})")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def test_manual_opds_request():
    """Ручной тест OPDS запроса"""
    
    print("\n=== Ручной тест OPDS ===")
    
    # Пробуем разные OPDS URL
    opds_urls = [
        "http://flibusta.is/opds",
        "https://flibusta.is/opds",
        "http://flibusta.site/opds",
        "https://flibusta.site/opds"
    ]
    
    for base_url in opds_urls:
        print(f"\nТестируем: {base_url}")
        
        try:
            # Пробуем получить корневой каталог
            response = requests.get(base_url, timeout=10)
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Доступен")
                
                # Пробуем поиск
                search_url = f"{base_url}/search?searchTerm=Пушкин"
                search_response = requests.get(search_url, timeout=10)
                print(f"Поиск статус: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    print(f"✅ Поиск работает")
                    print(f"Размер ответа: {len(search_response.content)} байт")
                else:
                    print(f"❌ Поиск не работает")
            else:
                print(f"❌ Недоступен")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    print("🚀 Запуск детальной диагностики Flibusta\n")
    
    # Проверяем подключение к БД
    try:
        book_count = Book.objects.count()
        print(f"📊 Текущее количество книг в БД: {book_count}")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        sys.exit(1)
    
    # Запускаем тесты
    test_manual_opds_request()
    test_flibusta_direct()
    test_alternative_search()
    
    print("\n✅ Диагностика завершена!")