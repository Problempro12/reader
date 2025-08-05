#!/usr/bin/env python
"""
Тест для анализа HTML-структуры Flibusta
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def test_flibusta_html():
    """Тест HTML-структуры Flibusta"""
    
    print("=== Анализ HTML-структуры Flibusta ===")
    
    # Базовые URL для тестирования
    base_urls = [
        'http://flibusta.is',
        'http://flibusta.site',
        'http://flibustahezeous3.onion'  # Tor адрес
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for base_url in base_urls:
        print(f"\n🔍 Тестирование: {base_url}")
        
        try:
            # Тест главной страницы
            print("   Проверка главной страницы...")
            response = session.get(base_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Главная страница доступна (статус: {response.status_code})")
                
                # Тест поиска
                search_url = f"{base_url}/booksearch?ask=Пушкин"
                print(f"   Проверка поиска: {search_url}")
                
                search_response = session.get(search_url, timeout=10)
                if search_response.status_code == 200:
                    print(f"   ✅ Поиск работает (статус: {search_response.status_code})")
                    
                    # Анализ HTML структуры
                    soup = BeautifulSoup(search_response.content, 'html.parser')
                    
                    print(f"   📄 Анализ HTML:")
                    print(f"      Title: {soup.title.text if soup.title else 'Нет title'}")
                    
                    # Ищем различные возможные структуры
                    structures_to_check = [
                        ('div.book-item', 'Блоки книг'),
                        ('a[href*="/b/"]', 'Ссылки на книги'),
                        ('table tr', 'Строки таблицы'),
                        ('ul li', 'Элементы списка'),
                        ('div', 'Все div элементы'),
                        ('a', 'Все ссылки')
                    ]
                    
                    for selector, description in structures_to_check:
                        elements = soup.select(selector)
                        print(f"      {description}: {len(elements)} элементов")
                        
                        if len(elements) > 0 and len(elements) < 20:  # Показываем только если не слишком много
                            for i, elem in enumerate(elements[:5]):
                                text = elem.get_text(strip=True)[:100]
                                href = elem.get('href', '')
                                print(f"        {i+1}. {text} {href}")
                    
                    # Сохраняем HTML для анализа
                    with open(f'/tmp/flibusta_search_{base_url.replace("://", "_").replace(".", "_")}.html', 'w', encoding='utf-8') as f:
                        f.write(search_response.text)
                    print(f"   💾 HTML сохранен в /tmp/")
                    
                else:
                    print(f"   ❌ Поиск недоступен (статус: {search_response.status_code})")
                    
            else:
                print(f"   ❌ Главная страница недоступна (статус: {response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Таймаут при подключении к {base_url}")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Ошибка подключения к {base_url}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        time.sleep(1)  # Пауза между запросами

def test_opds_structure():
    """Тест OPDS структуры"""
    
    print("\n=== Анализ OPDS структуры ===")
    
    opds_urls = [
        'http://flibusta.is/opds/search?searchTerm=Пушкин',
        'http://flibusta.site/opds/search?searchTerm=Пушкин'
    ]
    
    session = requests.Session()
    
    for opds_url in opds_urls:
        print(f"\n🔍 Тестирование OPDS: {opds_url}")
        
        try:
            response = session.get(opds_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ OPDS доступен (статус: {response.status_code})")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                # Сохраняем XML для анализа
                with open(f'/tmp/flibusta_opds_{opds_url.split("//")[1].split("/")[0]}.xml', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 OPDS XML сохранен в /tmp/")
                
                # Показываем первые 500 символов
                print(f"   📄 Первые 500 символов:")
                print(f"   {response.text[:500]}...")
                
            else:
                print(f"   ❌ OPDS недоступен (статус: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Ошибка OPDS: {e}")
        
        time.sleep(1)

if __name__ == '__main__':
    print("🚀 Запуск анализа Flibusta\n")
    
    test_flibusta_html()
    test_opds_structure()
    
    print("\n✅ Анализ завершен!")
    print("\n📁 Проверьте сохраненные файлы в /tmp/ для детального анализа")