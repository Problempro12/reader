#!/usr/bin/env python
import requests
import json

# Поиск книги
print("=== Поиск книги через Tor ===")
data = {
    'query': 'фантастика',
    'sources': ['flibusta'],
    'use_tor': True,
    'limit': 1
}

response = requests.post('http://localhost:8000/api/books/search_external/', json=data)
print(f"Статус поиска: {response.status_code}")

if response.status_code == 200:
    books = response.json()
    print("Найденные книги:")
    print(json.dumps(books, ensure_ascii=False, indent=2)[:1000])
    
    if books.get('flibusta') and len(books['flibusta']) > 0:
        book = books['flibusta'][0]
        print(f"\n=== Импорт книги: {book['title']} ===")
        
        import_data = {
            'book_data': book,
            'source': 'flibusta'
        }
        
        import_response = requests.post('http://localhost:8000/api/books/import_external/', json=import_data)
        print(f"Импорт статус: {import_response.status_code}")
        print(f"Импорт ответ: {import_response.text[:500]}")
    else:
        print("Книги не найдены")
else:
    print(f"Ошибка поиска: {response.text}")