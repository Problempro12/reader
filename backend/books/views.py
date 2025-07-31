from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Book, Genre, AgeCategory, Author
from .serializers import BookSerializer, GenreSerializer, AgeCategorySerializer
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from .google_books_api import GoogleBooksAPI
import asyncio

class BookListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

class GenreListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

class AgeCategoryListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgeCategorySerializer
    queryset = AgeCategory.objects.all()

class ImportBooksView(APIView):
    def post(self, request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.import_books())
        return Response({'result': result})

    async def import_books(self):
        api = GoogleBooksAPI()
        CATEGORIES = ['fiction', 'fantasy', 'science fiction', 'mystery', 'romance']
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        for category in CATEGORIES:
            books = await api.search_books(f"subject:{category}", max_results=10)
            for google_book in books:
                try:
                    book_data = await api.get_book_details(google_book.get('id'))
                    if not book_data:
                        continue
                    volume_info = book_data.get('volumeInfo', {})
                    title = volume_info.get('title')
                    authors = volume_info.get('authors', [])
                    categories = volume_info.get('categories', [])
                    if not title or not authors:
                        continue
                    author_name = authors[0]
                    author, _ = Author.objects.get_or_create(name=author_name)
                    genre_name = categories[0] if categories else 'Художественная литература'
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    age_category, _ = AgeCategory.objects.get_or_create(name='Для взрослых')
                    # Проверка на существование книги
                    if Book.objects.filter(title=title, author=author).exists():
                        total_skipped += 1
                        continue
                    cover = volume_info.get('imageLinks', {}).get('thumbnail', '')
                    description = volume_info.get('description', '')
                    Book.objects.create(
                        title=title,
                        author=author,
                        cover=cover,
                        description=description,
                        genre=genre,
                        age_category=age_category,
                        is_premium=False,
                        rating=volume_info.get('averageRating', 0.0),
                        series=volume_info.get('series', ''),
                        translator=volume_info.get('translator', ''),
                    )
                    total_imported += 1
                except Exception as e:
                    total_errors += 1
                    continue
        return {
            'imported': total_imported,
            'skipped': total_skipped,
            'errors': total_errors
        }

# Добавь остальные вьюхи по аналогии, если нужно (UserBook, Vote, ReadingProgress и т.д.)
