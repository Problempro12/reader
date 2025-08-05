from django.core.management.base import BaseCommand
from books.models import Book

class Command(BaseCommand):
    help = 'Проверяет данные книг в базе данных'
    
    def handle(self, *args, **options):
        books = Book.objects.all()
        
        self.stdout.write(f'Всего книг в БД: {books.count()}')
        
        if books.count() == 0:
            self.stdout.write(self.style.WARNING('В базе данных нет книг'))
            return
        
        self.stdout.write('\n=== Проверка данных книг ===')
        
        for i, book in enumerate(books[:5]):  # Показываем первые 5 книг
            self.stdout.write(f'\n📚 Книга {i+1}:')
            self.stdout.write(f'  ID: {book.id}')
            self.stdout.write(f'  Название: {book.title}')
            self.stdout.write(f'  Автор: {book.author.name}')
            
            # Проверяем описание
            if book.description:
                desc_preview = book.description[:100] + '...' if len(book.description) > 100 else book.description
                self.stdout.write(f'  Описание: {desc_preview}')
                self.stdout.write(f'  Длина описания: {len(book.description)} символов')
            else:
                self.stdout.write(self.style.WARNING('  Описание: ОТСУТСТВУЕТ'))
            
            # Проверяем содержимое
            if book.content:
                content_preview = book.content[:100] + '...' if len(book.content) > 100 else book.content
                self.stdout.write(f'  Содержимое: {content_preview}')
                self.stdout.write(f'  Длина содержимого: {len(book.content)} символов')
            else:
                self.stdout.write(self.style.WARNING('  Содержимое: ОТСУТСТВУЕТ'))
            
            # Дополнительная информация
            self.stdout.write(f'  Создано: {book.created_at}')
        
        # Статистика
        books_with_description = books.exclude(description__isnull=True).exclude(description__exact='').count()
        books_with_content = books.exclude(content__isnull=True).exclude(content__exact='').count()
        
        self.stdout.write('\n=== Статистика ===')
        self.stdout.write(f'Книг с описанием: {books_with_description} из {books.count()}')
        self.stdout.write(f'Книг с содержимым: {books_with_content} из {books.count()}')
        
        if books.count() > 5:
            self.stdout.write(f'\n(Показаны первые 5 книг из {books.count()})')