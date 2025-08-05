#!/usr/bin/env python3
import requests
import json

url = 'http://localhost:8000/api/books/search_external/'
data = {
    'query': 'python',
    'sources': ['flibusta'],  # Только Flibusta
    'use_tor': False,
    'limit': 5
}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")