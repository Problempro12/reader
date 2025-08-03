from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, UserBookViewSet, ReadingProgressViewSet, BookListView

router = DefaultRouter()
router.register(r'', BookViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'user-books', UserBookViewSet, basename='user-book')
router.register(r'reading-progress', ReadingProgressViewSet, basename='reading-progress')

urlpatterns = [
    path('', include(router.urls)),
]