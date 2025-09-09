from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, UserBookViewSet, ReadingProgressViewSet, BookListView, search_external_books_view, import_external_book_view

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'user-books', UserBookViewSet, basename='user-book')
router.register(r'reading-progress', ReadingProgressViewSet, basename='reading-progress')
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search_external/', search_external_books_view, name='search-external-books'),
    path('import_external/', import_external_book_view, name='import-external-book'),
    path('import_category_books/', BookViewSet.as_view({'post': 'import_category_books'}), name='import-category-books'),
]