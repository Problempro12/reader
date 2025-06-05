from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('scrape-litres/', views.ScrapeLitresView.as_view(), name='scrape-litres'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('age-categories/', views.AgeCategoryListView.as_view(), name='age-category-list'),
    path('votes/', views.VoteCreateView.as_view(), name='vote-create'),
    path('progress/', views.ProgressCreateView.as_view(), name='progress-create'),
    path('weekly-results/', views.WeeklyResultListView.as_view(), name='weekly-result-list'),
] 