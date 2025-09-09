#!/usr/bin/env python
"""
Тест импорта книг через API эндпоинт
"""

import requests
import json

def test_category_import():
    """Тестирует импорт книг через API"""
    
    # URL для API эндпоинта
    api_url = "http://localhost:8001/api/books/import_category_books/"
    
    # Попробуем несколько известных URL категорий
    test_urls = [
        # История
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genre/20",
        # Классика
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genre/21",
        # Поэзия
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genre/22",
        # Документальная литература
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/opds/genre/23"
    ]
    
    # Количество книг для импорта
    import_count = 5
    
    all_tests_successful = True
    
    for i, category_url in enumerate(test_urls, 1):
        print(f"\n=== Тест {i}: {category_url} ===")
        
        # Данные для POST запроса
        data = {
            "category_url": category_url,
            "count": import_count
        }
        
        test_passed = False
        try:
            print(f"📤 Отправляем запрос на импорт {import_count} книг...")
            response = requests.post(api_url, json=data, timeout=120)
            
            print(f"📥 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Успешно!")
                print(f"   Импортировано: {result.get('imported_count', 0)}")
                print(f"   Найдено всего: {result.get('total_found', 0)}")
                
                errors = result.get('errors', [])
                if errors:
                    print(f"   Ошибки ({len(errors)}):")
                    for error in errors:
                        print(f"     • {error}")
                
                # Если импорт прошел успешно, отмечаем тест как успешный
                test_passed = True
                    
            else:
                print(f"❌ Ошибка: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Детали: {error_data.get('error', 'Неизвестная ошибка')}")
                except:
                    print(f"   Ответ: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"⏰ Таймаут запроса (120 секунд) для {category_url}")
            all_tests_successful = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            all_tests_successful = False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            all_tests_successful = False
        
        if not test_passed:
            all_tests_successful = False
    
    if all_tests_successful:
        print(f"\n✅ Все тестовые URL сработали успешно!")
        return True
    else:
        print(f"\n❌ Некоторые тестовые URL не сработали")
        return False

if __name__ == '__main__':
    print("🚀 Тестирование импорта книг через API")
    print("📋 Будем тестировать несколько категорий...")
    
    success = test_category_import()
    
    if success:
        print("\n✅ Тестирование завершено успешно!")
    else:
        print("\n❌ Тестирование не удалось")