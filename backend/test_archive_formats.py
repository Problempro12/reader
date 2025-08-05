#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
import django
django.setup()

from books.external_sources import FlibustaTorClient
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_different_archive_formats():
    """Тест обработки разных форматов архивов"""
    print("=== Тест обработки разных форматов архивов ===")
    
    # Создаем клиент с Tor
    client = FlibustaTorClient(use_tor=True)
    
    # Поиск книги
    query = "Чехов"
    print(f"\nПоиск книги: {query}")
    
    books = client.search_books(query, limit=1)
    
    if not books:
        print("Книги не найдены")
        return
    
    book = books[0]
    print(f"\nНайдена книга: {book.get('title')}")
    print(f"Автор: {book.get('author')}")
    
    download_links = book.get('download_links', [])
    print(f"\nДоступные форматы: {len(download_links)}")
    
    # Тестируем разные форматы
    formats_to_test = ['fb2', 'txt', 'epub']
    
    for format_type in formats_to_test:
        print(f"\n=== Тест формата {format_type.upper()} ===")
        
        # Ищем доступный формат
        available_format = None
        for link in download_links:
            link_format = link.get('format', '')
            if (link_format == format_type or 
                link_format == f"{format_type}+zip" or
                link_format.startswith(f"{format_type}+")):
                available_format = link_format
                break
        
        if available_format:
            print(f"Найден формат: {available_format}")
            
            # Скачиваем
            content = client.download_book(book, format_preference=format_type)
            
            if content:
                print(f"✓ Успешно скачано в формате {format_type}")
                print(f"Размер: {len(content)} символов")
                
                # Проверяем содержимое
                preview = content[:200] if len(content) > 200 else content
                print(f"Начало содержимого: {repr(preview)}")
                
                # Проверяем формат
                if format_type == 'fb2':
                    if content.strip().startswith('<?xml') and 'FictionBook' in content:
                        print("✓ Валидный FB2")
                    else:
                        print("⚠ Не FB2 формат")
                elif format_type == 'txt':
                    if not content.strip().startswith('<'):
                        print("✓ Текстовый формат")
                    else:
                        print("⚠ Возможно не чистый текст")
                elif format_type == 'epub':
                    if 'epub' in content.lower() or content.strip().startswith('<?xml'):
                        print("✓ EPUB содержимое")
                    else:
                        print("⚠ Неожиданный формат EPUB")
                        
            else:
                print(f"✗ Не удалось скачать {format_type}")
        else:
            print(f"Формат {format_type} недоступен")

if __name__ == "__main__":
    test_different_archive_formats()