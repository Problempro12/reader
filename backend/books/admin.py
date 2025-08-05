from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.management import call_command
from django.utils.html import format_html
from .models import Book, Author, UserBook, ReadingProgress, BookVote, WeeklyBook
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

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
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-by-category/', self.admin_site.admin_view(self.import_by_category_view), name='books_import_by_category'),
            path('update-covers/', self.admin_site.admin_view(self.update_covers_view), name='books_update_covers'),
            path('run-import-category/', self.admin_site.admin_view(self.run_import_category), name='books_run_import_category'),
            path('run-update-covers/', self.admin_site.admin_view(self.run_update_covers), name='books_run_update_covers'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_buttons'] = [
            {
                'url': 'import-by-category/',
                'title': 'Импорт книг по категориям',
                'class': 'addlink'
            },
            {
                'url': 'update-covers/',
                'title': 'Обновить обложки',
                'class': 'changelink'
            }
        ]
        return super().changelist_view(request, extra_context=extra_context)
    
    def import_by_category_view(self, request):
        """Страница для импорта книг по категориям"""
        if request.method == 'GET':
            # Список популярных категорий
            categories = [
                'Фантастика',
                'Детективы',
                'Классика',
                'Романы',
                'Приключения',
                'Научная фантастика',
                'Фэнтези',
                'Исторические романы',
                'Современная проза',
                'Поэзия'
            ]
            
            context = {
                'title': 'Импорт книг по категориям',
                'categories': categories,
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request),
            }
            return render(request, 'admin/books/import_by_category.html', context)
    
    def update_covers_view(self, request):
        """Страница для обновления обложек"""
        if request.method == 'GET':
            context = {
                'title': 'Обновление обложек книг',
                'opts': self.model._meta,
                'has_view_permission': self.has_view_permission(request),
                'total_books': Book.objects.count(),
                'books_without_covers': Book.objects.filter(cover_url__isnull=True).count() + Book.objects.filter(cover_url='').count(),
            }
            return render(request, 'admin/books/update_covers.html', context)
    
    def run_import_category(self, request):
        """Запуск импорта книг по категории"""
        if request.method == 'POST':
            category = request.POST.get('category')
            count = int(request.POST.get('count', 10))
            skip_existing = request.POST.get('skip_existing') == 'on'
            
            if not category:
                return JsonResponse({'error': 'Категория не выбрана'}, status=400)
            
            try:
                # Захватываем вывод команды
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    call_command(
                        'import_books_by_category',
                        category=category,
                        count=count,
                        skip_existing=skip_existing
                    )
                
                output = stdout_capture.getvalue()
                errors = stderr_capture.getvalue()
                
                return JsonResponse({
                    'success': True,
                    'output': output,
                    'errors': errors,
                    'message': f'Импорт завершен для категории "{category}"'
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Ошибка при импорте: {str(e)}'
                }, status=500)
        
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    def run_update_covers(self, request):
        """Запуск обновления обложек"""
        if request.method == 'POST':
            force = request.POST.get('force') == 'on'
            only_missing = request.POST.get('only_missing') == 'on'
            
            try:
                # Захватываем вывод команды
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                args = []
                if force:
                    args.append('--force')
                if only_missing:
                    args.append('--only-missing')
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    call_command('update_book_covers', *args)
                
                output = stdout_capture.getvalue()
                errors = stderr_capture.getvalue()
                
                return JsonResponse({
                    'success': True,
                    'output': output,
                    'errors': errors,
                    'message': 'Обновление обложек завершено'
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Ошибка при обновлении обложек: {str(e)}'
                }, status=500)
        
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

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
