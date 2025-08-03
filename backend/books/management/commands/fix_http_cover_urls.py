from django.core.management.base import BaseCommand
from books.models import Book

class Command(BaseCommand):
    help = 'Fix HTTP cover URLs by converting them to HTTPS'
    
    def handle(self, *args, **options):
        # Найти все книги с HTTP URL обложек
        books_with_http_urls = Book.objects.filter(
            cover_url__startswith='http://'
        )
        
        updated_count = 0
        
        for book in books_with_http_urls:
            old_url = book.cover_url
            # Конвертируем HTTP в HTTPS
            book.cover_url = book.cover_url.replace('http://', 'https://')
            book.save()
            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated book "{book.title}": {old_url} -> {book.cover_url}'
                )
            )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING('No books with HTTP cover URLs found.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} books with HTTPS cover URLs.'
                )
            )