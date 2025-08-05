#!/usr/bin/env python
"""
Тест проверки всех ссылок в OPDS-записях Flibusta
"""

import os
import sys
import django
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.external_sources import FlibustaTorClient

def test_opds_links():
    """Тест проверки всех ссылок в OPDS"""
    print("=== Тест проверки всех ссылок в OPDS-записях ===")
    
    client = FlibustaTorClient(use_tor=False)
    
    try:
        # Выполняем поиск книг напрямую
        search_url = f"{client.base_url}/opds/search?searchType=books&searchTerm=Пушкин"
        print(f"URL поиска книг: {search_url}")
        
        response = requests.get(search_url, timeout=30)
        
        if response.status_code == 200:
            # Парсим XML
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', ns)
            print(f"Найдено записей книг: {len(entries)}")
            
            for i, entry in enumerate(entries[:2]):  # Берем первые 2 записи
                title = entry.find('atom:title', ns)
                print(f"\n📚 Книга {i+1}: {title.text if title is not None else 'Без названия'}")
                
                # Проверяем все ссылки
                links = entry.findall('atom:link', ns)
                print(f"  Всего ссылок: {len(links)}")
                
                for j, link in enumerate(links):
                    rel = link.get('rel', 'нет rel')
                    href = link.get('href', 'нет href')
                    link_type = link.get('type', 'нет type')
                    
                    print(f"    Ссылка {j+1}:")
                    print(f"      rel: {rel}")
                    print(f"      href: {href}")
                    print(f"      type: {link_type}")
                    
                    # Проверяем, подходит ли для обложки
                    if 'image' in rel.lower() or 'thumbnail' in rel.lower():
                        print(f"      🖼️  ПОТЕНЦИАЛЬНАЯ ОБЛОЖКА!")
                    elif rel in ['http://opds-spec.org/acquisition', 'http://opds-spec.org/acquisition/open-access']:
                        print(f"      📥 Ссылка для скачивания")
                    elif rel == 'alternate':
                        print(f"      🔗 Альтернативная ссылка")
                    else:
                        print(f"      ❓ Другая ссылка (rel: {rel})")
                        
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            print(f"Ответ: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_opds_links()