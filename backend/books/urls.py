from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('<int:pk>/rating/', views.BookRatingView.as_view(), name='book-rating'),
    path('<int:pk>/rate/', views.BookRateView.as_view(), name='book-rate'),
    path('scrape-litres/', views.ScrapeLitresView.as_view(), name='scrape-litres'),
    path('run-import-script/', views.RunImportBooksView.as_view(), name='run-import-script'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('age-categories/', views.AgeCategoryListView.as_view(), name='age-category-list'),
    path('votes/', views.VoteCreateView.as_view(), name='vote-create'),
    path('progress/', views.ProgressCreateView.as_view(), name='progress-create'),
    path('progress/<int:pk>/', views.ProgressDetailView.as_view(), name='progress-detail'),
    path('weekly-results/', views.WeeklyResultListView.as_view(), name='weekly-result-list'),
    path('current-week/', views.CurrentWeekBookView.as_view(), name='current-week'),
    path('voting-candidates/', views.VotingCandidatesView.as_view(), name='voting-candidates'),
    path('user-votes/', views.UserVotesView.as_view(), name='user-votes'),
] 