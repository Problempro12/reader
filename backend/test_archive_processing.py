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

def test_archive_processing():
    """Тест обработки архивов при скачивании книг"""
    print("=== Тест обработки архивов при скачивании книг ===")
    
    # Создаем клиент с Tor
    client = FlibustaTorClient(use_tor=True)
    
    # Поиск книги
    query = "Пушкин Евгений Онегин"
    print(f"\nПоиск книги: {query}")
    
    books = client.search_books(query, limit=3)
    
    if not books:
        print("Книги не найдены")
        return
    
    print(f"Найдено книг: {len(books)}")
    
    for i, book in enumerate(books, 1):
        print(f"\n--- Книга {i} ---")
        print(f"Название: {book.get('title')}")
        print(f"Автор: {book.get('author')}")
        print(f"ID: {book.get('source_id')}")
        
        download_links = book.get('download_links', [])
        print(f"Доступные форматы: {len(download_links)}")
        
        for link in download_links:
            format_type = link.get('format')
            url = link.get('url')
            print(f"  - {format_type}: {url}")
            
            # Проверяем, что это zip-архив
            if '+zip' in format_type or 'zip' in format_type.lower():
                print(f"    ✓ Это архив: {format_type}")
        
        # Пробуем скачать первую книгу
        if i == 1:
            print(f"\n=== Скачивание книги '{book.get('title')}' ===")
            
            # Скачиваем в формате fb2 (который обычно в архиве)
            content = client.download_book(book, format_preference='fb2')
            
            if content:
                print(f"✓ Книга успешно скачана")
                print(f"Размер содержимого: {len(content)} символов")
                
                # Показываем начало содержимого
                preview = content[:500] if len(content) > 500 else content
                print(f"\nНачало содержимого:")
                print("-" * 50)
                print(preview)
                print("-" * 50)
                
                # Проверяем, что это FB2
                if content.strip().startswith('<?xml') and 'FictionBook' in content:
                    print("✓ Содержимое является валидным FB2 файлом")
                elif content.strip().startswith('<'):
                    print("⚠ Содержимое является XML, но возможно не FB2")
                else:
                    print("⚠ Содержимое не является XML/FB2")
                    
            else:
                print("✗ Не удалось скачать книгу")
            
            break

if __name__ == "__main__":
    test_archive_processing()