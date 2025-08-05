#!/usr/bin/env python

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('/Users/aleksandrkocergin/Documents/kpit.pw/reader/backend')

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.models import Book
from books.external_sources import ExternalBookSources

def demo_description_update():
    """Демонстрация обновления описания книги из Flibusta"""
    
    print("=== Демонстрация обновления описания книги из Flibusta ===")
    print()
    
    # Параметры для демонстрации
    book_id = 59  # ID книги в нашей базе данных
    external_id = "836962"  # ID книги в Flibusta
    
    try:
        # Получаем книгу из базы данных
        book = Book.objects.get(id=book_id)
        print(f"📚 Книга из базы данных:")
        print(f"   ID: {book.id}")
        print(f"   Название: {book.title}")
        print(f"   Автор: {book.author.name}")
        print(f"   Текущее описание: {book.description[:100] if book.description else 'Отсутствует'}...")
        print()
        
        # Создаем клиент для работы с внешними источниками
        external_sources = ExternalBookSources(use_tor_for_flibusta=True)
        
        # Получаем аннотацию из Flibusta
        print(f"🔍 Получение аннотации из Flibusta (ID: {external_id})...")
        description = external_sources.get_book_description(external_id)
        
        if description:
            print(f"✅ Аннотация получена успешно!")
            print(f"   Длина: {len(description)} символов")
            print(f"   Превью: {description[:200]}...")
            print()
            
            # Обновляем описание в базе данных
            print("💾 Обновление описания в базе данных...")
            old_description = book.description
            book.description = description
            book.save(update_fields=['description'])
            
            print(f"✅ Описание успешно обновлено!")
            print()
            
            # Показываем результат
            print("📊 Результат обновления:")
            print(f"   Старое описание: {old_description[:100] if old_description else 'Отсутствовало'}...")
            print(f"   Новое описание: {description[:100]}...")
            print(f"   Изменение размера: {len(old_description) if old_description else 0} → {len(description)} символов")
            
        else:
            print("❌ Аннотация не найдена или пуста")
            
    except Book.DoesNotExist:
        print(f"❌ Книга с ID {book_id} не найдена в базе данных")
    except Exception as e:
        print(f"❌ Ошибка при обновлении описания: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_description_update()