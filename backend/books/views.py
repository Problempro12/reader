from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Book, Author, UserBook, ReadingProgress, BookVote, WeeklyBook
from .serializers import BookSerializer, BookListSerializer, BookFrontendSerializer, AuthorSerializer, UserBookSerializer, ReadingProgressSerializer
# Google Books импорт удален - используем только Флибусту
from .external_sources import search_external_books, import_book_from_external_source, FlibustaTorClient

class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit objects"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for books"""
    queryset = Book.objects.all().select_related('author')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BookFrontendSerializer
        return BookSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by author if provided
        author_id = self.request.query_params.get('author_id', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Custom list method to return paginated response in expected format"""
        queryset = self.get_queryset()
        
        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 12))
        
        # Apply filters
        search = request.query_params.get('search', '')
        if search:
            search_lower = search.lower()
            # Filter books where title or author name contains search term (case-insensitive)
            filtered_books = []
            for book in queryset:
                if (search_lower in book.title.lower() or 
                    search_lower in book.author.name.lower()):
                    filtered_books.append(book.id)
            
            if filtered_books:
                queryset = queryset.filter(id__in=filtered_books)
            else:
                queryset = queryset.none()
        
        genre = request.query_params.get('genre', '')
        if genre:
            # Filter by genre using the same logic as in serializer
            genres = [
                "Художественная литература",
                "Фантастика", 
                "Детектив",
                "Роман",
                "Классика",
                "Приключения",
                "Драма",
                "Фэнтези"
            ]
            if genre in genres:
                genre_index = genres.index(genre)
                # Filter books where id % len(genres) == genre_index
                filtered_ids = [book.id for book in queryset if book.id % len(genres) == genre_index]
                queryset = queryset.filter(id__in=filtered_ids)
        
        age_category = request.query_params.get('ageCategory', '')
        if age_category:
            # Filter by age category using the same logic as in serializer
            age_categories = ["0+", "6+", "12+", "16+", "18+"]
            if age_category in age_categories:
                age_index = age_categories.index(age_category)
                # Filter books where id % len(age_categories) == age_index
                filtered_ids = [book.id for book in queryset if book.id % len(age_categories) == age_index]
                queryset = queryset.filter(id__in=filtered_ids)
        
        # Filter by rating
        rating = request.query_params.get('rating', '')
        if rating:
            try:
                min_rating = float(rating)
                # Filter books with average rating >= min_rating
                from django.db.models import Avg
                filtered_ids = []
                for book in queryset:
                    avg_rating = book.user_books.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
                    if avg_rating and avg_rating >= min_rating:
                        filtered_ids.append(book.id)
                queryset = queryset.filter(id__in=filtered_ids)
            except ValueError:
                pass  # Invalid rating value, ignore
        
        # Apply sorting
        sort_by = request.query_params.get('sortBy', '')
        if sort_by == 'rating':
            # Sort all books by average rating
            from django.db.models import Avg
            queryset_list = list(queryset)
            def get_avg_rating(book):
                avg_rating = book.user_books.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
                return avg_rating if avg_rating else 0.0
            queryset_list.sort(key=get_avg_rating, reverse=True)
            # Create a new queryset with sorted IDs
            sorted_ids = [book.id for book in queryset_list]
            # Use a custom ordering to preserve the sort
            from django.db.models import Case, When, IntegerField
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)], output_field=IntegerField())
            queryset = queryset.filter(id__in=sorted_ids).order_by(preserved)
        elif sort_by == 'newest':
            # Sort by ID descending (assuming higher ID = newer)
            queryset = queryset.order_by('-id')
        elif sort_by == 'alphabet':
            # Sort by title alphabetically
            queryset = queryset.order_by('title')
        
        # Paginate
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        
        # Serialize
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        return Response({
            'books': serializer.data,
            'total': paginator.count,
            'page': page,
            'limit': limit
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def content(self, request, pk=None):
        """Get book content for reading"""
        from .utils import get_book_content_from_external_sources
        from .external_sources import ExternalBookSources
        
        book = self.get_object()
        
        # Если контент пустой или содержит заглушку, пытаемся получить контент
        if not book.content or book.content == 'Содержимое книги будет добавлено позже.' or len(book.content.strip()) < 100:
            content_loaded = False
            
            # Если книга импортирована с Флибусты, пытаемся загрузить с Флибусты
            if book.source_type == 'flibusta' and book.source_id:
                 try:
                     external_sources = ExternalBookSources(use_tor_for_flibusta=True)
                     book_data = {
                         'source_id': book.source_id,
                         'title': book.title,
                         'download_links': []  # Будет получено через source_id
                     }
                     flibusta_content = external_sources.get_book_content('flibusta', book_data, 'fb2')
                     if flibusta_content and len(flibusta_content.strip()) > 100:
                         book.content = flibusta_content
                         book.save()
                         content_loaded = True
                 except Exception as e:
                     print(f"Ошибка загрузки с Флибусты: {e}")
            
            # Если не удалось загрузить с Флибусты, используем демо-контент
            if not content_loaded:
                demo_content = get_book_content_from_external_sources(book.title, book.author.name)
                if demo_content:
                    book.content = demo_content
                    book.save()
        
        content = book.content or 'Содержимое книги пока недоступно. Не удалось загрузить текст.'
        
        return Response({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'content': content
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def content_paginated(self, request, pk=None):
        """Get book content with pagination"""
        from .utils import paginate_book_content
        
        book = self.get_object()
        page = int(request.query_params.get('page', 1))
        words_per_page = int(request.query_params.get('words_per_page', 300))
        
        # Get full content first
        content_response = self.content(request, pk)
        full_content = content_response.data['content']
        
        # Paginate content
        paginated_data = paginate_book_content(full_content, page, words_per_page)
        
        return Response({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'current_page': paginated_data['current_page'],
            'total_pages': paginated_data['total_pages'],
            'content': paginated_data['content'],
            'has_next': paginated_data['has_next'],
            'has_previous': paginated_data['has_previous']
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def top_voted(self, request):
        """Get top 5 books by vote count"""
        limit = int(request.query_params.get('limit', 5))
        books = Book.objects.all().order_by('-vote_count')[:limit]
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def user_votes(self, request):
        """Get user's votes for books"""
        # Placeholder for actual logic to retrieve user votes
        # This would typically involve a separate voting model
        return Response({'detail': 'User votes endpoint not yet implemented.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def run_import_script(self, request):
        """Run the book import script."""
        # Placeholder for actual script execution logic
        try:
            # Example: call a function that runs the import script
            query = request.data.get('query', 'популярные книги')
            # Google Books импорт отключен - используем только Флибусту
            result = {'error': 'Google Books импорт отключен. Используйте поиск по внешним источникам.'}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_reading_stats(self, request):
        """Get comprehensive reading statistics for the user"""
        from django.db.models import Sum, Max
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        user = request.user
        
        # Get all user books
        user_books = UserBook.objects.filter(user=user)
        completed_books = user_books.filter(status=UserBook.Status.COMPLETED)
        
        # Calculate total pages read
        total_pages_read = 0
        
        # For completed books, count all pages
        for book in completed_books:
            if book.book.content:
                # Estimate total pages based on content length
                words_count = len(book.book.content.split())
                estimated_pages = max(1, words_count // 300)  # 300 words per page
                total_pages_read += estimated_pages
        
        # For books in progress, get current page from progress
        reading_books = user_books.filter(status=UserBook.Status.READING)
        for user_book in reading_books:
            try:
                # Get latest progress for this book
                latest_progress = ReadingProgress.objects.filter(
                    user_book=user_book
                ).order_by('-created_at').first()
                
                if latest_progress and latest_progress.current_page:
                    total_pages_read += latest_progress.current_page
            except:
                pass
        
        # Calculate reading streak (consecutive days with reading activity)
        reading_streak = 0
        if ReadingProgress.objects.filter(user_book__user=user).exists():
            # Get all unique dates when user made progress
            progress_dates = ReadingProgress.objects.filter(
                user_book__user=user
            ).dates('created_at', 'day').order_by('-created_at')
            
            if progress_dates:
                current_date = timezone.now().date()
                streak_count = 0
                
                # Check if user read today or yesterday (to account for timezone)
                latest_reading_date = progress_dates[0]
                if (current_date - latest_reading_date).days <= 1:
                    streak_count = 1
                    check_date = latest_reading_date - timedelta(days=1)
                    
                    # Count consecutive days backwards
                    for date in progress_dates[1:]:
                        if date == check_date:
                            streak_count += 1
                            check_date -= timedelta(days=1)
                        else:
                            break
                
                reading_streak = streak_count
        
        # Get total reading marks and calculate hours
        total_marks = ReadingProgress.objects.filter(user_book__user=user).count()
        total_hours = max(0, total_marks // 4)  # 4 marks = 1 hour
        
        return Response({
            'books_read': completed_books.count(),
            'pages_read': total_pages_read,
            'reading_streak': reading_streak,
            'total_hours': total_hours,
            'total_marks': total_marks
        })
    

    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Rate a book"""
        book = self.get_object()
        rating = request.data.get('rating')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update UserBook with rating
        user_book, created = UserBook.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'rating': rating}
        )
        
        if not created:
            user_book.rating = rating
            user_book.save()
        
        # Return updated book data with rating
        serializer = BookFrontendSerializer(book)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def rating(self, request, pk=None):
        """Get book rating information including user's rating"""
        book = self.get_object()
        
        # Calculate average rating and count
        from django.db.models import Avg, Count
        rating_stats = book.user_books.filter(rating__isnull=False).aggregate(
            average_rating=Avg('rating'),
            rating_count=Count('rating')
        )
        
        # Get user's rating if authenticated
        user_rating = None
        if request.user.is_authenticated:
            try:
                user_book = UserBook.objects.get(user=request.user, book=book)
                user_rating = user_book.rating
            except UserBook.DoesNotExist:
                user_rating = None
        
        return Response({
            'user_rating': user_rating,
            'average_rating': round(rating_stats['average_rating'], 1) if rating_stats['average_rating'] else 0.0,
            'rating_count': rating_stats['rating_count'] or 0
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        """Vote for a book"""
        book = self.get_object()
        
        # Check if user already voted for this book
        existing_vote = BookVote.objects.filter(user=request.user, book=book).first()
        if existing_vote:
            return Response({'error': 'You have already voted for this book'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vote
        BookVote.objects.create(user=request.user, book=book)
        
        # Update vote count
        book.vote_count = book.votes.count()
        book.save()
        
        return Response({
            'message': 'Vote added successfully',
            'vote_count': book.vote_count,
            'user_voted': True
        })

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def remove_vote(self, request, pk=None):
        """Remove vote for a book"""
        book = self.get_object()
        
        # Find and delete user's vote
        vote = BookVote.objects.filter(user=request.user, book=book).first()
        if not vote:
            return Response({'error': 'You have not voted for this book'}, status=status.HTTP_400_BAD_REQUEST)
        
        vote.delete()
        
        # Update vote count
        book.vote_count = book.votes.count()
        book.save()
        
        return Response({
            'message': 'Vote removed successfully',
            'vote_count': book.vote_count,
            'user_voted': False
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def vote_info(self, request, pk=None):
        """Get vote information for a book"""
        book = self.get_object()
        
        # Check if user voted (if authenticated)
        user_voted = False
        if request.user.is_authenticated:
            user_voted = BookVote.objects.filter(user=request.user, book=book).exists()
        
        return Response({
            'vote_count': book.vote_count,
            'user_voted': user_voted
        })

    def retrieve(self, request, pk=None):
        """Get a specific book by ID"""
        book = self.get_object()
        serializer = BookFrontendSerializer(book)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current_week(self, request):
        """Get the current book of the week"""
        try:
            # Get the most recent weekly book
            weekly_book = WeeklyBook.objects.select_related('book', 'book__author').latest('week_start')
            
            # Check if it's still current (within the week)
            from datetime import datetime, timedelta
            now = datetime.now().date()
            week_end = weekly_book.week_start + timedelta(days=7)
            
            if now <= week_end:
                # Still current
                book_data = BookFrontendSerializer(weekly_book.book).data
                book_data['week_start'] = weekly_book.week_start
                book_data['week_end'] = week_end
                book_data['is_current'] = True
                return Response(book_data)
            else:
                # Week has ended, no current book
                return Response({
                    'message': 'No current book of the week',
                    'is_current': False
                }, status=status.HTTP_404_NOT_FOUND)
                
        except WeeklyBook.DoesNotExist:
            return Response({
                'message': 'No book of the week has been set',
                'is_current': False
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def top(self, request):
        """Get top books (most popular)"""
        # For now, return books ordered by ID (newest first)
        # In a real app, this would be based on ratings, views, etc.
        books = Book.objects.all().order_by('-id')[:10]
        serializer = BookFrontendSerializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def recommended(self, request):
        """Get recommended books"""
        # Simple recommendation: return random books
        # In a real app, this would use ML or user preferences
        books = Book.objects.all().order_by('?')[:10]
        serializer = BookFrontendSerializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def genres(self, request):
        """Get list of all available genres"""
        # For now, return a static list of genres
        # In real implementation, this would be extracted from books
        genres = [
            "Художественная литература",
            "Фантастика",
            "Детектив",
            "Роман",
            "Классика",
            "Приключения",
            "Драма",
            "Комедия",
            "Триллер",
            "Фэнтези"
        ]
        return Response(genres)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def flibusta_categories(self, request):
        """Get all available categories from Flibusta"""
        try:
            client = FlibustaTorClient(use_tor=True)
            
            # Получаем все жанры напрямую с HTML-страницы
            all_categories = client.get_all_genres()
            
            # Преобразуем формат для соответствия ожидаемой структуре
            formatted_categories = []
            for category in all_categories:
                formatted_categories.append({
                    'name': category['name'],
                    'url': category['url']
                })
            
            return Response({
                'success': True,
                'categories': formatted_categories,
                'count': len(formatted_categories)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'categories': [],
                'count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def age_categories(self, request):
        """Get list of all available age categories"""
        # For now, return a static list of age categories
        # In real implementation, this would be extracted from books
        age_categories = [
            "0+",
            "6+",
            "12+",
            "16+",
            "18+"
        ]
        return Response(age_categories)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def import_category_books(self, request):
        """Массовый импорт книг из категории Flibusta"""
        from django.db import transaction
        from .models import Author
        
        try:
            category_url = request.data.get('category_url')
            count = request.data.get('count', 10)
            
            if not category_url:
                return Response({
                    'success': False,
                    'error': 'Category URL is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate count
            try:
                count = int(count)
                if count <= 0 or count > 50:
                    return Response({
                        'success': False,
                        'error': 'Count must be between 1 and 50'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'Invalid count value'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Import books using the external sources client
            from .external_sources import ExternalBookSources
            client = FlibustaTorClient(use_tor=True)
            sources = ExternalBookSources(use_tor_for_flibusta=True)
            books_data = client.browse_books_by_category(category_url, sort_by_popularity=True, limit=count)
            
            imported_count = 0
            errors = []
            
            with transaction.atomic():
                for book_data in books_data:
                    try:
                        # Check if book already exists
                        existing_book = Book.objects.filter(
                            title=book_data.get('title', ''),
                            author__name=book_data.get('author', '')
                        ).first()
                        
                        if existing_book:
                            continue
                        
                        # Create or get author
                        author_name = book_data.get('author', 'Неизвестный автор')
                        author, created = Author.objects.get_or_create(
                            name=author_name,
                            defaults={'bio': ''}
                        )
                        
                        # Download full book content
                        content = import_book_from_external_source(book_data, 'flibusta', 'fb2', use_tor=True)
                        
                        if content:
                            # Получаем аннотацию книги
                            description = book_data.get('description', '')
                            book_id = book_data.get('source_id') or book_data.get('id')
                            if book_id and not description:
                                description = sources.get_book_description(book_id)
                            
                            # Create book in database with full content
                            book = Book.objects.create(
                                title=book_data.get('title', 'Без названия'),
                                author=author,
                                description=description or '',
                                content=content,
                                cover_url=book_data.get('cover_url', ''),
                                genre=book_data.get('genre', 'Общее'),
                                source_id=book_id or '',
                                source_type='flibusta'
                            )
                            
                            imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Error importing '{book_data.get('title', 'Unknown')}': {str(e)}")
            
            return Response({
                'success': True,
                'imported_count': imported_count,
                'total_found': len(books_data),
                'errors': errors[:5] if errors else []  # Limit errors to first 5
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def delete_all_books(self, request):
        """Удаление всех книг из базы данных"""
        try:
            # Подсчитываем количество книг перед удалением
            total_books = Book.objects.count()
            
            # Удаляем все книги
            Book.objects.all().delete()
            
            return Response({
                'success': True,
                'message': f'Successfully deleted {total_books} books',
                'deleted_count': total_books
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def voting_candidates(self, request):
        """Get books that are candidates for voting"""
        # Placeholder for actual logic to determine voting candidates
        # For now, return a few books
        candidates = Book.objects.all()[:5] # Example: first 5 books
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)


# Отдельные функции представлений для внешних источников
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def search_external_books_view(request):
    """Поиск книг во внешних источниках"""
    try:
        query = request.data.get('query', '')
        sources = request.data.get('sources', ['flibusta'])
        use_tor = request.data.get('use_tor', True)
        limit = request.data.get('limit', 10)
        
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = search_external_books(query, sources, use_tor, limit)
        return Response(results)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def import_external_book_view(request):
    """Импорт книги из внешнего источника с сохранением в БД"""
    try:
        book_data = request.data.get('book_data')
        source = request.data.get('source', 'flibusta')
        download_format = request.data.get('download_format', 'fb2')
        
        if not book_data:
            return Response({'error': 'Book data is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем содержимое книги
        content = import_book_from_external_source(book_data, source, download_format, use_tor=True)
        
        if not content:
            return Response({'error': 'Failed to download book content'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Получаем аннотацию книги
        from .external_sources import ExternalBookSources
        sources = ExternalBookSources(use_tor_for_flibusta=True)
        description = None
        book_id = book_data.get('source_id') or book_data.get('id')
        if book_id:
            description = sources.get_book_description(book_id)
        
        # Создаем или получаем автора
        author_name = book_data.get('author', 'Неизвестный автор')
        author, created = Author.objects.get_or_create(
            name=author_name,
            defaults={'bio': ''}
        )
        
        # Проверяем, не существует ли уже такая книга
        existing_book = Book.objects.filter(
            title=book_data.get('title', ''),
            author=author
        ).first()
        
        if existing_book:
            return Response({
                'success': False,
                'error': 'Book already exists in database',
                'book_id': existing_book.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Создаем новую книгу
        book = Book.objects.create(
            title=book_data.get('title', ''),
            author=author,
            content=content,
            description=description or book_data.get('description', ''),
            genre=book_data.get('genre', ''),
            cover_url=book_data.get('cover_url', ''),
            source_id=book_data.get('id', ''),
            source_type=source
        )
        
        from .serializers import BookSerializer
        serializer = BookSerializer(book)
        return Response({
            'success': True,
            'book': serializer.data,
            'message': 'Book imported successfully'
        })
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for authors"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]

class UserBookViewSet(viewsets.ModelViewSet):
    """ViewSet for user books"""
    serializer_class = UserBookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserBook.objects.filter(user=self.request.user).select_related('book', 'book__author')
    
    @action(detail=False, methods=['post'])
    def add_to_list(self, request):
        """Add a book to user's list"""
        book_id = request.data.get('book_id')
        status = request.data.get('status', UserBook.Status.PLANNED)
        
        if not book_id:
            return Response({'error': 'Book ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        book = get_object_or_404(Book, id=book_id)
        
        # Check if book already in user's library
        user_book, created = UserBook.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'status': status}
        )
        
        if not created:
            user_book.status = status
            user_book.save()
        
        serializer = self.get_serializer(user_book)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_to_library(self, request):
        """Add a book to user's library (legacy endpoint)"""
        return self.add_to_list(request)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update status of a book in user's library"""
        user_book = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_book.status = new_status
        user_book.save()
        
        serializer = self.get_serializer(user_book)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def remove_from_list(self, request):
        """Remove a book from user's list"""
        book_id = request.data.get('book_id')
        
        if not book_id:
            return Response({'error': 'Book ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_book = UserBook.objects.get(user=request.user, book_id=book_id)
            user_book.delete()
            return Response({'message': 'Book removed from list successfully'})
        except UserBook.DoesNotExist:
            return Response({'error': 'Book not found in user list'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def user_lists(self, request):
        """Get all user's lists with books grouped by status"""
        user_books = self.get_queryset()
        
        lists = {
            'planned': [],
            'reading': [],
            'completed': [],
            'dropped': []
        }
        
        for user_book in user_books:
            book_data = {
                'id': user_book.book.id,
                'title': user_book.book.title,
                'author': {
                    'id': user_book.book.author.id,
                    'name': user_book.book.author.name
                },
                'cover_url': user_book.book.cover_url,
                'added_at': user_book.added_at,
                'rating': user_book.rating
            }
            lists[user_book.status].append(book_data)
        
        return Response(lists)
    
    @action(detail=False, methods=['get'])
    def list_by_status(self, request):
        """Get books by specific status"""
        status_param = request.query_params.get('status')
        
        if not status_param:
            return Response({'error': 'Status parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if status_param not in [choice[0] for choice in UserBook.Status.choices]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_books = self.get_queryset().filter(status=status_param)
        serializer = self.get_serializer(user_books, many=True)
        return Response(serializer.data)

class ReadingProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for reading progress"""
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReadingProgress.objects.filter(
            user_book__user=self.request.user
        ).select_related('user_book', 'user_book__book')
    
    def perform_create(self, serializer):
        # Ensure user_book belongs to the current user
        user_book_id = self.request.data.get('user_book')
        user_book = get_object_or_404(UserBook, id=user_book_id, user=self.request.user)
        
        # If book status is not 'reading', update it
        if user_book.status != UserBook.Status.READING:
            user_book.status = UserBook.Status.READING
            user_book.save()
        
        serializer.save()
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def save_page_progress(self, request):
        """Save reading progress for a specific page"""
        from .utils import calculate_reading_position
        
        book_id = request.data.get('book_id')
        current_page = request.data.get('current_page', 1)
        total_pages = request.data.get('total_pages', 1)
        words_per_page = request.data.get('words_per_page', 300)
        
        if not book_id:
            return Response({'error': 'book_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = Book.objects.get(id=book_id)
            user_book, created = UserBook.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={'status': UserBook.Status.READING}
            )
            
            # Calculate position in text based on page
            position = calculate_reading_position(book.content, current_page, words_per_page)
            
            # Always create new reading progress entry
            progress = ReadingProgress.objects.create(
                user_book=user_book,
                position=position,
                current_page=current_page,
                total_pages=total_pages
            )
            
            # Update user_book status if needed
            if user_book.status != UserBook.Status.READING:
                user_book.status = UserBook.Status.READING
                user_book.save()
            
            return Response({
                'success': True,
                'current_page': progress.current_page,
                'total_pages': progress.total_pages,
                'progress_percentage': progress.progress_percentage
            })
            
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_page_progress(self, request):
        """Get reading progress for a book"""
        from .utils import get_page_from_position
        
        book_id = request.query_params.get('book_id')
        words_per_page = int(request.query_params.get('words_per_page', 300))
        
        if not book_id:
            return Response({'error': 'book_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = Book.objects.get(id=book_id)
            user_book = UserBook.objects.filter(user=request.user, book=book).first()
            
            if not user_book:
                # No progress yet, return first page
                return Response({
                    'current_page': 1,
                    'total_pages': 1,
                    'progress_percentage': 0
                })
            
            progress = ReadingProgress.objects.filter(user_book=user_book).order_by('-created_at').first()
            
            if not progress:
                # No progress yet, return first page
                return Response({
                    'current_page': 1,
                    'total_pages': 1,
                    'progress_percentage': 0
                })
            
            # If we have old progress without page info, calculate from position
            if progress.current_page == 1 and progress.total_pages == 1 and progress.position > 0:
                progress.current_page = get_page_from_position(book.content, progress.position, words_per_page)
                # Calculate total pages
                from .utils import paginate_book_content
                pagination_info = paginate_book_content(book.content, 1, words_per_page)
                progress.total_pages = pagination_info['total_pages']
                progress.save()
            
            return Response({
                'current_page': progress.current_page,
                'total_pages': progress.total_pages,
                'progress_percentage': progress.progress_percentage
            })
            
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookListView(generics.ListAPIView):
    """View для списка книг (используется админкой)"""
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookFrontendSerializer
    permission_classes = [permissions.AllowAny]
    
    def list(self, request, *args, **kwargs):
        # Получаем параметры запроса
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        search = request.GET.get('search', '')
        genre = request.GET.get('genre', '')
        age_category = request.GET.get('ageCategory', '')
        
        # Базовый queryset
        queryset = self.get_queryset()
        
        # Применяем фильтры
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(author__name__icontains=search)
            )
        
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
            
        if age_category:
            queryset = queryset.filter(age_category__icontains=age_category)
        
        # Пагинация
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        
        # Сериализация
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        return Response({
            'books': serializer.data,
            'total': paginator.count,
            'page': page,
            'limit': limit
        })
