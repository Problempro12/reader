from django.contrib import admin
from .models import Book, Genre, AgeCategory, Author

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'age_category', 'rating', 'is_premium')
    list_filter = ('genre', 'age_category', 'is_premium')
    search_fields = ('title', 'author__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
<<<<<<< HEAD
    list_per_page = 1000
=======
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'description', 'cover')
        }),
        ('Классификация', {
            'fields': ('genre', 'age_category', 'is_premium')
        }),
        ('Дополнительная информация', {
            'fields': ('series', 'translator', 'technical')
        }),
        ('Рейтинг', {
            'fields': ('rating', 'litres_rating')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AgeCategory)
class AgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
