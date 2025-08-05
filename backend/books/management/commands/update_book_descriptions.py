from django.core.management.base import BaseCommand
from books.models import Book
from books.external_sources import ExternalBookSources
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Обновляет описания книг, получая аннотации из Flibusta по внешнему ID'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--book-id',
            type=int,
            help='ID конкретной книги для обновления описания'
        )
        parser.add_argument(
            '--external-id',
            type=str,
            help='Внешний ID книги в Flibusta для получения аннотации'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно обновить описание, даже если оно уже существует'
        )
        parser.add_argument(
            '--only-missing',
            action='store_true',
            help='Обновить только книги без описания'
        )
    
    def handle(self, *args, **options):
        book_id = options.get('book_id')
        external_id = options.get('external_id')
        force = options['force']
        only_missing = options['only_missing']
        
        # Если указан внешний ID, обновляем конкретную книгу
        if external_id:
            if book_id:
                try:
                    book = Book.objects.get(id=book_id)
                    self.update_single_book_description(book, external_id, force)
                except Book.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Книга с ID {book_id} не найдена')
                    )
                    return
            else:
                self.stdout.write(
                    self.style.ERROR('При указании external-id необходимо также указать book-id')
                )
                return
        else:
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
                    books = Book.objects.filter(description__isnull=True) | Book.objects.filter(description='')
                    self.stdout.write(f'Обновление описаний для {books.count()} книг без описания...')
                else:
                    books = Book.objects.all()
                    self.stdout.write(f'Обновление описаний для всех {books.count()} книг...')
            
            self.update_multiple_books_descriptions(books, force, only_missing)
    
    def update_single_book_description(self, book, external_id, force):
        """Обновление описания одной книги по внешнему ID"""
        try:
            # Проверяем, нужно ли обновлять описание
            if not force and book.description:
                self.stdout.write(
                    self.style.WARNING(f'Пропущено (уже есть описание): {book.title} - {book.author.name}')
                )
                return
            
            self.stdout.write(f'Обновляю описание: {book.title} - {book.author.name} (External ID: {external_id})')
            
            # Инициализируем источник книг
            book_source = ExternalBookSources(use_tor_for_flibusta=True)
            
            # Получаем описание
            description = book_source.get_book_description(external_id)
            
            if description and description.strip():
                old_description = book.description or 'отсутствует'
                book.description = description.strip()
                book.save(update_fields=['description'])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Обновлено: {book.title}\n'
                        f'  Старое описание: {old_description[:100] if old_description != "отсутствует" else old_description}...\n'
                        f'  Новое описание: {description[:100]}...\n'
                        f'  Длина: {len(description)} символов'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Описание не найдено для: {book.title}')
                )
                
        except Exception as e:
            logger.error(f'Ошибка при обновлении описания книги {book.title}: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Ошибка при обновлении {book.title}: {str(e)}')
            )
    
    def update_multiple_books_descriptions(self, books, force, only_missing):
        """Обновление описаний множества книг"""
        try:
            # Инициализируем источник книг
            book_source = ExternalBookSources(use_tor_for_flibusta=True)
            
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for book in books:
                try:
                    # Проверяем, нужно ли обновлять описание
                    if not force and not only_missing and book.description:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Пропущено (уже есть описание): {book.title} - {book.author.name}')
                        )
                        continue
                    
                    self.stdout.write(f'Попытка обновления описания: {book.title} - {book.author.name}')
                    
                    # Здесь нужно будет добавить логику поиска внешнего ID
                    # Пока что пропускаем, так как нет связи между внутренним и внешним ID
                    self.stdout.write(
                        self.style.WARNING(
                            f'- Пропущено: {book.title} (нет связи с внешним ID Flibusta)'
                        )
                    )
                    skipped_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f'Ошибка при обработке книги {book.title}: {str(e)}')
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при обработке {book.title}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nОбновление описаний завершено:\n'
                    f'- Обновлено: {updated_count} книг\n'
                    f'- Пропущено: {skipped_count} книг\n'
                    f'- Ошибок: {error_count} книг\n'
                    f'- Всего обработано: {updated_count + skipped_count + error_count} книг'
                )
            )
            
        except Exception as e:
            logger.error(f'Критическая ошибка при обновлении описаний: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Критическая ошибка: {str(e)}')
            )