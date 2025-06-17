from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet,
    VotingCandidatesView,
    UserVotesView,
    CurrentWeekBookView,
    BookListView,
    BookDetailView,
    GenreListView,
    AgeCategoryListView,
    VoteCreateView,
    ProgressCreateView,
    WeeklyResultListView,
    ProgressDetailView,
    BookRatingView,
    BookRateView
)

router = DefaultRouter()
router.register('books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('books/voting-candidates/', VotingCandidatesView.as_view(), name='voting-candidates'),
    path('books/user-votes/', UserVotesView.as_view(), name='user-votes'),
    path('books/current-week/', CurrentWeekBookView.as_view(), name='current-week'),
    path('books/list/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('genres/', GenreListView.as_view(), name='genre-list'),
    path('age-categories/', AgeCategoryListView.as_view(), name='age-category-list'),
    path('votes/', VoteCreateView.as_view(), name='vote-create'),
    path('progress/', ProgressCreateView.as_view(), name='progress-create'),
    path('weekly-results/', WeeklyResultListView.as_view(), name='weekly-results'),
    path('progress/<int:pk>/', ProgressDetailView.as_view(), name='progress-detail'),
    path('books/<int:pk>/rating/', BookRatingView.as_view(), name='book-rating'),
    path('books/<int:pk>/rate/', BookRateView.as_view(), name='book-rate'),
] 