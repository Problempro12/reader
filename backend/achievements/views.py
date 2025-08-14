from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer

class AchievementViewSet(viewsets.ModelViewSet):
    """ViewSet for achievements"""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user achievements"""
    serializer_class = UserAchievementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserAchievement.objects.filter(
            user=self.request.user
        ).select_related('achievement').order_by('-earned_at')

class CheckAchievementsView(generics.GenericAPIView):
    """View to check and award achievements"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        awarded = []
        
        # Get all achievements that the user doesn't have yet
        user_achievement_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
        achievements = Achievement.objects.exclude(id__in=user_achievement_ids)
        
        # Check each achievement
        for achievement in achievements:
            if self.check_achievement_requirements(user, achievement):
                # Award the achievement
                user_achievement = UserAchievement.objects.create(
                    user=user,
                    achievement=achievement
                )
                awarded.append(UserAchievementSerializer(user_achievement).data)
        
        return Response({
            'awarded_achievements': awarded
        })
    
    def check_achievement_requirements(self, user, achievement):
        """Check if user meets the requirements for an achievement"""
        from books.models import UserBook, ReadingProgress
        
        requirement = achievement.requirement
        category = achievement.category
        
        # Проверка достижений по чтению
        if category in [Achievement.Category.READING, Achievement.Category.BOOKS, Achievement.Category.SOCIAL]:
            if 'books_read' in requirement:
                books_read = UserBook.objects.filter(
                    user=user, 
                    status=UserBook.Status.COMPLETED
                ).count()
                return books_read >= requirement['books_read']
                
            if 'progress_marks' in requirement:
                progress_marks = ReadingProgress.objects.filter(
                    user_book__user=user
                ).count()
                return progress_marks >= requirement['progress_marks']
                
            if 'books_rated' in requirement:
                books_rated = UserBook.objects.filter(
                    user=user,
                    rating__isnull=False
                ).count()
                return books_rated >= requirement['books_rated']
                
            if 'books_in_library' in requirement:
                books_in_library = UserBook.objects.filter(user=user).count()
                return books_in_library >= requirement['books_in_library']
        
        # Пока что другие типы достижений не реализованы
        if category == Achievement.Category.OTHER:
            # Заглушка для специальных достижений
            return False
        
        return False
