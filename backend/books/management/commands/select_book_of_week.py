from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from books.models import Book, WeeklyBook, BookVote
from django.db import transaction

class Command(BaseCommand):
    help = 'Select book of the week from top voted books'

    def handle(self, *args, **options):
        # Получаем текущую дату
        now = timezone.now().date()
        
        # Находим понедельник текущей недели
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        # Проверяем, есть ли уже книга недели для этой недели
        existing_weekly_book = WeeklyBook.objects.filter(
            week_start=week_start,
            week_end=week_end
        ).first()
        
        if existing_weekly_book:
            self.stdout.write(
                self.style.WARNING(
                    f'Book of the week already exists for {week_start} - {week_end}: {existing_weekly_book.book.title}'
                )
            )
            return
        
        # Находим книгу с наибольшим количеством голосов
        top_book = Book.objects.filter(
            is_book_of_week=False
        ).order_by('-vote_count').first()
        
        if not top_book:
            self.stdout.write(
                self.style.ERROR('No books available for selection')
            )
            return
        
        if top_book.vote_count == 0:
            self.stdout.write(
                self.style.WARNING('Top book has no votes, skipping selection')
            )
            return
        
        # Выполняем операции в транзакции
        with transaction.atomic():
            # Сбрасываем статус "книга недели" у всех книг
            Book.objects.filter(is_book_of_week=True).update(is_book_of_week=False)
            
            # Создаем запись о книге недели
            weekly_book = WeeklyBook.objects.create(
                book=top_book,
                week_start=week_start,
                week_end=week_end,
                votes_at_selection=top_book.vote_count
            )
            
            # Устанавливаем книгу как книгу недели
            top_book.is_book_of_week = True
            top_book.save()
            
            # Сбрасываем голоса у всех книг
            BookVote.objects.all().delete()
            Book.objects.all().update(vote_count=0)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully selected "{top_book.title}" as book of the week '
                f'for {week_start} - {week_end} with {weekly_book.votes_at_selection} votes'
            )
        )