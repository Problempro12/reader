from django.contrib import admin
from .models import Book, Author, UserBook, ReadingProgress, BookVote, WeeklyBook

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'vote_count', 'is_book_of_week', 'published_date', 'created_at')
    list_filter = ('author', 'is_book_of_week', 'published_date')
    search_fields = ('title', 'author__name', 'description')
    date_hierarchy = 'published_date'
    readonly_fields = ('vote_count',)

@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'rating', 'added_at')
    list_filter = ('status', 'rating', 'added_at')
    search_fields = ('user__username', 'user__email', 'book__title')
    date_hierarchy = 'added_at'

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user_book', 'position', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_book__user__username', 'user_book__book__title')
    date_hierarchy = 'created_at'

@admin.register(BookVote)
class BookVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'book__title')
    date_hierarchy = 'created_at'

@admin.register(WeeklyBook)
class WeeklyBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'week_start', 'week_end', 'votes_at_selection', 'created_at')
    list_filter = ('week_start', 'week_end', 'created_at')
    search_fields = ('book__title',)
    date_hierarchy = 'week_start'
    readonly_fields = ('votes_at_selection', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('book', 'book__author')
