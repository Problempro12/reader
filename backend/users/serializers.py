from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class BookStatsSerializer(serializers.Serializer):
    """Serializer for user's book statistics"""
    read_count = serializers.IntegerField(default=0)
    planning_count = serializers.IntegerField(default=0)
    reading_count = serializers.IntegerField(default=0)
    dropped_count = serializers.IntegerField(default=0)
    total_count = serializers.IntegerField(default=0)
    progress_marks_count = serializers.IntegerField(default=0)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    stats = BookStatsSerializer(read_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_premium', 'premium_expiration_date', 
                  'hide_ads', 'avatar_url', 'about', 'stats', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'email', 'is_premium', 'premium_expiration_date', 
                           'hide_ads', 'is_staff', 'is_superuser']
    
    def get_stats(self, obj):
        # Импортируем здесь, чтобы избежать циклического импорта
        from books.models import UserBook
        
        stats = {
            'read_count': UserBook.objects.filter(user=obj, status='read').count(),
            'planning_count': UserBook.objects.filter(user=obj, status='planning').count(),
            'reading_count': UserBook.objects.filter(user=obj, status='reading').count(),
            'dropped_count': UserBook.objects.filter(user=obj, status='dropped').count(),
        }
        stats['total_count'] = sum(stats.values())
        return stats

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user