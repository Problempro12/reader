#!/usr/bin/env python
import os
import sys
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from users.models import User
from books.models import UserBook, Book

def add_test_ratings():
    user = User.objects.first()
    if not user:
        print("Нет пользователей в системе")
        return
    
    books = Book.objects.all()[:10]
    created_count = 0
    
    for book in books:
        user_book, created = UserBook.objects.get_or_create(
            user=user, 
            book=book, 
            defaults={
                'rating': random.randint(1, 5), 
                'status': 'read'
            }
        )
        if created:
            created_count += 1
        elif user_book.rating is None:
            user_book.rating = random.randint(1, 5)
            user_book.save()
            created_count += 1
    
    print(f'Добавлены/обновлены рейтинги для {created_count} книг')
    
    # Показать текущие рейтинги
    user_books = UserBook.objects.filter(rating__isnull=False)[:5]
    for ub in user_books:
        print(f'Книга ID {ub.book.id}: {ub.book.title[:30]}... - Рейтинг: {ub.rating}')

if __name__ == '__main__':
    add_test_ratings()