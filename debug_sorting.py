#!/usr/bin/env python3
"""
Скрипт для отладки сортировки книг
"""

import requests
import json

def test_sorting():
    base_url = 'http://127.0.0.1:8000/api/books/'
    
    print("=== Тестирование сортировки книг ===")
    
    # Тест 1: Без сортировки
    print("\n1. Запрос без сортировки:")
    response1 = requests.get(base_url, params={'limit': 8})
    if response1.status_code == 200:
        books1 = response1.json()['books']
        print(f"URL: {response1.url}")
        print("Результат:")
        for i, book in enumerate(books1, 1):
            print(f"  {i}. ID: {book['id']}, Rating: {book['rating']}, Title: {book['title'][:40]}...")
    else:
        print(f"Ошибка: {response1.status_code}")
    
    # Тест 2: С сортировкой по рейтингу
    print("\n2. Запрос с сортировкой по рейтингу:")
    response2 = requests.get(base_url, params={'sortBy': 'rating', 'limit': 8})
    if response2.status_code == 200:
        books2 = response2.json()['books']
        print(f"URL: {response2.url}")
        print("Результат:")
        for i, book in enumerate(books2, 1):
            print(f"  {i}. ID: {book['id']}, Rating: {book['rating']}, Title: {book['title'][:40]}...")
    else:
        print(f"Ошибка: {response2.status_code}")
    
    # Сравнение
    print("\n3. Сравнение результатов:")
    if response1.status_code == 200 and response2.status_code == 200:
        order1 = [book['id'] for book in books1]
        order2 = [book['id'] for book in books2]
        
        print(f"Порядок без сортировки: {order1}")
        print(f"Порядок с сортировкой:  {order2}")
        
        if order1 == order2:
            print("❌ ПРОБЛЕМА: Порядок книг одинаковый! Сортировка не работает.")
        else:
            print("✅ Порядок книг разный. Сортировка работает.")
            
        # Проверим, действительно ли книги отсортированы по рейтингу
        ratings2 = [book['rating'] for book in books2]
        is_sorted = all(ratings2[i] >= ratings2[i+1] for i in range(len(ratings2)-1))
        
        if is_sorted:
            print("✅ Книги действительно отсортированы по убыванию рейтинга.")
        else:
            print("❌ ПРОБЛЕМА: Книги НЕ отсортированы по убыванию рейтинга.")
            print(f"Рейтинги: {ratings2}")
    
    # Тест 3: Другие варианты сортировки
    print("\n4. Тест других вариантов сортировки:")
    for sort_type in ['newest', 'alphabet']:
        print(f"\n  Сортировка '{sort_type}':")
        response = requests.get(base_url, params={'sortBy': sort_type, 'limit': 5})
        if response.status_code == 200:
            books = response.json()['books']
            print(f"  URL: {response.url}")
            for book in books:
                print(f"    ID: {book['id']}, Title: {book['title'][:30]}...")
        else:
            print(f"  Ошибка: {response.status_code}")

if __name__ == '__main__':
    test_sorting()