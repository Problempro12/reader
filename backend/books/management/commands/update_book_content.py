from django.core.management.base import BaseCommand
from books.models import Book
from books.utils import get_real_book_content_from_external_sources

class Command(BaseCommand):
    help = 'Обновляет содержимое всех книг, получая реальные тексты из внешних источников (Флибуста, LibGen)'
    
    def handle(self, *args, **options):
        books = Book.objects.all()
        updated_count = 0
        
        self.stdout.write(f'Найдено {books.count()} книг для обновления...')
        
        for book in books:
            self.stdout.write(f'Обновляю книгу: {book.title} - {book.author}')
            
            # Получаем новое содержимое из внешних источников
            new_content = get_real_book_content_from_external_sources(book.title, book.author.name)
            
            if new_content and new_content != book.content:
                book.content = new_content
                book.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Обновлено: {book.title} (длина: {len(new_content)} символов)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Пропущено: {book.title} (контент не изменился или недоступен)')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nОбновление завершено. Обновлено книг: {updated_count} из {books.count()}')
        )