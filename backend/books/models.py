from django.db import models

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class AgeCategory(models.Model):
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.URLField()
    description = models.TextField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    age_category = models.ForeignKey(AgeCategory, on_delete=models.SET_NULL, null=True)
    is_premium = models.BooleanField(default=False)
    rating = models.FloatField(default=0)
    litres_rating = models.JSONField(null=True, blank=True)
    series = models.CharField(max_length=200, blank=True)
    translator = models.CharField(max_length=200, blank=True)
    technical = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
