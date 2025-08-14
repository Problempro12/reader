from django.db import models
from django.conf import settings

class Achievement(models.Model):
    """Achievement model"""
    class Category(models.TextChoices):
        READING = 'READING', 'Reading'
        BOOKS = 'BOOKS', 'Books'
        SOCIAL = 'SOCIAL', 'Social'
        OTHER = 'OTHER', 'Other'
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.ImageField(upload_to='achievements/', null=True, blank=True)
    points = models.IntegerField(default=10)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    requirement = models.JSONField(help_text='JSON with requirements for achievement')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    """User's earned achievement"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='users')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"
