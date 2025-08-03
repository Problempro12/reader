from django.contrib import admin
from .models import Achievement, UserAchievement

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points', 'id')
    list_filter = ('category', 'points')
    search_fields = ('title', 'description', 'category')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('earned_at', 'achievement__category')
    search_fields = ('user__username', 'user__email', 'achievement__title')
    date_hierarchy = 'earned_at'
