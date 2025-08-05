from django.core.management.base import BaseCommand
from books.models import Book
from books.external_sources import ExternalBookSources
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Принудительно обновляет обложки всех книг из внешних источников'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--book-id',
            type=int,
            help='ID конкретной книги для обновления обложки (если не указан, обновляются все книги)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно обновить обложки даже у книг, у которых уже есть обложка'
        )
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Обновить обложки только у книг без обложек'
        )
    
    def handle(self, *args, **options):
        book_id = options.get('book_id')
        force = options['force']
        only_missing = options['only_missing']
        
        # Определяем какие книги обрабатывать
        if book_id:
            try:
                books = Book.objects.filter(id=book_id)
                if not books.exists():
                    self.stdout.write(
                        self.style.ERROR(f'Книга с ID {book_id} не найдена')
                    )
                    return
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при поиске книги: {str(e)}')
                )
                return
        else:
            if only_missing:
                books = Book.objects.filter(cover_url__isnull=True) | Book.objects.filter(cover_url='')
                self.stdout.write(f'Обновление обложек для {books.count()} книг без обложек...')
            else:
                books = Book.objects.all()
                self.stdout.write(f'Обновление обложек для всех {books.count()} книг...')
        
        try:
            # Инициализируем источник книг
            book_source = ExternalBookSources()
            
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for book in books:
                try:
                    # Проверяем, нужно ли обновлять обложку
                    if not force and not only_missing and book.cover_url:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Пропущено (уже есть обложка): {book.title} - {book.author.name}')
                        )
                        continue
                    
                    self.stdout.write(f'Обновляю обложку: {book.title} - {book.author.name}')
                    
                    # Получаем URL обложки
                    cover_url = book_source.get_book_cover_url(
                        book_id=str(book.id),
                        title=book.title,
                        author=book.author.name
                    )
                    
                    if cover_url and cover_url != book.cover_url:
                        old_cover = book.cover_url or 'отсутствует'
                        book.cover_url = cover_url
                        book.save(update_fields=['cover_url'])
                        updated_count += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Обновлено: {book.title}\n'
                                f'  Старая обложка: {old_cover}\n'
                                f'  Новая обложка: {cover_url}'
                            )
                        )
                    elif cover_url == book.cover_url:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Пропущено (обложка не изменилась): {book.title}')
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Не удалось найти обложку: {book.title} - {book.author.name}')
                        )
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f'Ошибка при обновлении обложки для книги {book.title}: {str(e)}')
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при обновлении {book.title}: {str(e)}')
                    )
                    continue
            
            # Выводим итоговую статистику
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nОбновление обложек завершено:\n'
                    f'- Обновлено: {updated_count} обложек\n'
                    f'- Пропущено: {skipped_count} книг\n'
                    f'- Ошибок: {error_count} книг\n'
                    f'- Всего обработано: {updated_count + skipped_count + error_count} книг'
                )
            )
            
        except Exception as e:
            logger.error(f'Критическая ошибка при обновлении обложек: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Критическая ошибка: {str(e)}')
            )