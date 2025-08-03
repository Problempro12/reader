from rest_framework import serializers
from .models import Achievement, UserAchievement

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for the Achievement model"""
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'icon_url', 'points', 'category', 'requirement', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for the UserAchievement model"""
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'earned_at']
        read_only_fields = ['id', 'user', 'earned_at']