from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model"""
    email = models.EmailField(_('email address'), unique=True)
    avatar_url = models.ImageField(upload_to='avatars/', null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    premium_expiration_date = models.DateTimeField(null=True, blank=True)
    hide_ads = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
