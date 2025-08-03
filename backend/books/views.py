from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Book, Author, UserBook, ReadingProgress, BookVote, WeeklyBook
from .serializers import BookSerializer, BookListSerializer, BookFrontendSerializer, AuthorSerializer, UserBookSerializer, ReadingProgressSerializer
from .utils import import_books_from_google_books

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
    
    def retrieve(self, request, pk=None):
        """Get a single book by ID"""
        book = get_object_or_404(Book, pk=pk)
        serializer = self.get_serializer(book)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def current_week(self, request):
        """Get the book of the current week"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Получаем текущую дату
        now = timezone.now().date()
        
        # Находим понедельник текущей недели
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        # Ищем книгу недели для текущей недели
        weekly_book = WeeklyBook.objects.filter(
            week_start=week_start,
            week_end=week_end
        ).first()
        
        if weekly_book:
            serializer = self.get_serializer(weekly_book.book)
            data = serializer.data
            data['is_book_of_week'] = True
            data['week_start'] = weekly_book.week_start
            data['week_end'] = weekly_book.week_end
            data['votes_at_selection'] = weekly_book.votes_at_selection
            return Response(data)
        
        # Если нет книги недели, ищем текущую книгу недели по флагу
        book = Book.objects.filter(is_book_of_week=True).first()
        if book:
            serializer = self.get_serializer(book)
            data = serializer.data
            data['is_book_of_week'] = True
            return Response(data)
        
        return Response({'detail': 'No book of the week selected'}, status=404)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def top(self, request):
        """Get top rated books"""
        limit = int(request.query_params.get('limit', 5))
        # For now, return first books as top books
        # In real implementation, this would be sorted by rating
        books = Book.objects.all()[:limit]
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def recommended(self, request):
        """Get recommended books"""
        limit = int(request.query_params.get('limit', 5))
        # For now, return random books as recommended
        # In real implementation, this would be based on user preferences
        books = Book.objects.all().order_by('?')[:limit]
        serializer = self.get_serializer(books, many=True)
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

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def voting_candidates(self, request):
        """Get books that are candidates for voting"""
        # Placeholder for actual logic to determine voting candidates
        # For now, return a few books
        candidates = Book.objects.all()[:5] # Example: first 5 books
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)
    
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
            result = import_books_from_google_books(query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    def add_to_library(self, request):
        """Add a book to user's library"""
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
