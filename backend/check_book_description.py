#!/usr/bin/env python

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient
from bs4 import BeautifulSoup

def check_book_description(book_id):
    """Проверка описания книги на Flibusta"""
    try:
        print(f"=== Проверка описания книги ID {book_id} на Flibusta ===")
        
        # Создаем клиент с Tor для правильного onion-адреса
        client = FlibustaTorClient(use_tor=True)
        
        # Получаем страницу книги
        book_url = f"http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/b/{book_id}"
        print(f"Запрос к: {book_url}")
        
        response = client.session.get(book_url, timeout=30)
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Проверяем title страницы
            title_tag = soup.find('title')
            print(f"Title страницы: {title_tag.text if title_tag else 'Не найден'}")
            
            # Ищем meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                print(f"Meta description: {meta_desc.get('content')}")
            else:
                print("Meta description: Не найден")
            
            # Ищем описание в различных местах
            print("\n=== Поиск описания в HTML ===")
            
            # Ищем в div с классом или id, содержащим description, summary, annotation
            desc_containers = soup.find_all(['div', 'p', 'span'], 
                                           class_=lambda x: x and any(word in x.lower() for word in ['desc', 'summary', 'annotation', 'about']))
            
            if desc_containers:
                print(f"Найдено {len(desc_containers)} потенциальных контейнеров описания:")
                for i, container in enumerate(desc_containers[:5]):
                    text = container.get_text().strip()
                    if len(text) > 20:
                        print(f"  {i+1}. {text[:200]}...")
            
            # Ищем все div элементы с текстом
            all_divs = soup.find_all('div')
            print(f"\nВсего div элементов: {len(all_divs)}")
            
            # Показываем первые несколько div с содержательным текстом
            content_divs = []
            for div in all_divs:
                text = div.get_text().strip()
                if len(text) > 50 and not any(skip in text.lower() for skip in ['навигация', 'меню', 'поиск', 'copyright']):
                    content_divs.append(text)
            
            print(f"Div элементы с содержательным текстом (первые 5):")
            for i, text in enumerate(content_divs[:5]):
                print(f"  {i+1}. {text[:300]}...")
                
        else:
            print(f"Ошибка: получен статус {response.status_code}")
            
    except Exception as e:
        print(f"Ошибка при проверке описания: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Проверяем книгу с ID 59
    check_book_description("59")