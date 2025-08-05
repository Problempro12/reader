#!/usr/bin/env python
"""
Простой тест API поиска внешних книг
"""

import requests
import json

def test_api():
    url = "http://localhost:8000/api/books/search_external/"
    
    # Тест с пустыми источниками (должен вернуть пустой результат быстро)
    data = {
        "query": "Пушкин",
        "sources": [],  # Пустой список источников
        "use_tor": False,
        "limit": 2
    }
    
    try:
        print("Отправляем запрос к API...")
        response = requests.post(url, json=data, timeout=5)
        print(f"Статус ответа: {response.status_code}")
        print(f"Содержимое ответа: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Результат в JSON: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except requests.exceptions.Timeout:
        print("Таймаут запроса")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_api()