from django.urls import path
from . import views
from .views import ImportBooksView

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
    path('run-import-script/', ImportBooksView.as_view(), name='run-import-script'),
]