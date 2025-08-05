from django.core.management.base import BaseCommand
from books.models import Book, Author
from books.external_sources import ExternalBookSources
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Импортирует книги по категориям из Флибусты'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            required=True,
            help='Категория книг для импорта (например: "Фантастика", "Детективы", "Классика")'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество книг для импорта (по умолчанию: 10)'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропускать уже существующие книги'
        )
    
    def handle(self, *args, **options):
        category = options['category']
        count = options['count']
        skip_existing = options['skip_existing']
        
        self.stdout.write(f'Импорт {count} книг из категории "{category}"...')
        
        try:
            # Инициализируем источник книг
            book_source = ExternalBookSources()
            
            # Получаем список книг по категории
            if category.startswith('http'):
                # Если передан URL flibusta.is, преобразуем в onion-адрес
                if 'flibusta.is' in category:
                    from books.external_config import FLIBUSTA_CONFIG
                    onion_url = FLIBUSTA_CONFIG['onion_url']
                    category = category.replace('https://flibusta.is', onion_url).replace('http://flibusta.is', onion_url)
                    self.stdout.write(f'Преобразован URL в onion-адрес: {category}')
                books_data = book_source.flibusta.browse_books_by_category(category, limit=count * 2)
            else:
                # Если передано название категории, ищем по названию
                books_data = book_source.search_books_by_category(category, limit=count * 2)  # Берем больше для фильтрации
            
            if not books_data:
                self.stdout.write(
                    self.style.ERROR(f'Не найдено книг в категории "{category}"')
                )
                return
            
            imported_count = 0
            skipped_count = 0
            
            for book_data in books_data:
                if imported_count >= count:
                    break
                    
                title = book_data.get('title', '').strip()
                author_name = book_data.get('author', '').strip()
                
                if not title or not author_name:
                    continue
                
                # Проверяем, существует ли уже такая книга
                if skip_existing:
                    existing_book = Book.objects.filter(
                        title__iexact=title,
                        author__name__iexact=author_name
                    ).first()
                    
                    if existing_book:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Пропущено (уже существует): {title} - {author_name}')
                        )
                        continue
                
                try:
                    # Создаем или получаем автора
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={'bio': f'Автор книги "{title}"'}
                    )
                    
                    # Используем категорию как жанр в поле genre модели Book
                    genre_name = category
                    
                    # Получаем содержимое книги
                    content = book_source.get_book_content(
                        book_data=book_data,
                        format_type='fb2'
                    )
                    
                    if not content:
                        self.stdout.write(
                            self.style.WARNING(f'Не удалось получить содержимое: {title} - {author_name}')
                        )
                        continue
                    
                    # Получаем обложку
                    cover_url = book_source.get_book_cover_url(book_data.get('id', ''), title, author_name)
                    
                    # Создаем книгу
                    book = Book.objects.create(
                        title=title,
                        author=author,
                        description=book_data.get('description', f'Книга "{title}" автора {author_name}'),
                        content=content,
                        cover_url=cover_url or '',
                        genre=genre_name
                    )
                    
                    imported_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Импортировано: {title} - {author_name} (ID: {book.id})')
                    )
                    
                except Exception as e:
                    logger.error(f'Ошибка при импорте книги {title}: {str(e)}')
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при импорте: {title} - {str(e)}')
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nИмпорт завершен:\n'
                    f'- Импортировано: {imported_count} книг\n'
                    f'- Пропущено: {skipped_count} книг\n'
                    f'- Категория: {category}'
                )
            )
            
        except Exception as e:
            logger.error(f'Критическая ошибка при импорте: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Критическая ошибка: {str(e)}')
            )