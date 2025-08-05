#!/usr/bin/env python
"""
Скрипт для обновления обложек книг
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.cover_sources import update_existing_books_covers
from books.models import Book
from django.db import models

def main():
    print("=== Обновление обложек книг ===")
    print()
    
    # Проверяем подключение к базе данных
    try:
        total_books = Book.objects.count()
        print(f"📚 Всего книг в базе: {total_books}")
        
        # Считаем книги без обложек
        books_without_covers = Book.objects.filter(
            models.Q(cover_url__isnull=True) | 
            models.Q(cover_url='') | 
            models.Q(cover_url='/placeholder-book.svg')
        ).count()
        
        books_with_real_covers = Book.objects.exclude(
            models.Q(cover_url__isnull=True) | 
            models.Q(cover_url='') | 
            models.Q(cover_url='/placeholder-book.svg')
        ).count()
        
        print(f"🖼️  Книг с реальными обложками: {books_with_real_covers}")
        print(f"📋 Книг без обложек/с заглушками: {books_without_covers}")
        print()
        
        if books_without_covers == 0:
            print("✅ Все книги уже имеют обложки!")
            return
        
        print(f"🔄 Начинаем обновление обложек для {books_without_covers} книг...")
        print()
        
        # Обновляем обложки
        updated_count = update_existing_books_covers()
        
        print()
        print(f"✅ Обновление завершено! Обработано книг: {updated_count}")
        
        # Финальная статистика
        books_with_real_covers_after = Book.objects.exclude(
            models.Q(cover_url__isnull=True) | 
            models.Q(cover_url='') | 
            models.Q(cover_url='/placeholder-book.svg')
        ).count()
        
        books_with_placeholders = Book.objects.filter(
            cover_url='/placeholder-book.svg'
        ).count()
        
        print(f"📊 Итоговая статистика:")
        print(f"   • Книг с реальными обложками: {books_with_real_covers_after}")
        print(f"   • Книг с заглушками: {books_with_placeholders}")
        print(f"   • Найдено новых обложек: {books_with_real_covers_after - books_with_real_covers}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()