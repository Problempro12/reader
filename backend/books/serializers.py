from rest_framework import serializers
from .models import Book, Genre, AgeCategory

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'coverUrl',
            'genreId', 'ageCategoryId', 'rating',
            'isPremium', 'litresRating', 'litresRatingCount',
            'series', 'translator', 'volume', 'year', 'isbn',
            'copyrightHolder', 'createdAt', 'updatedAt'
        ]

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class AgeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeCategory
        fields = ['id', 'name'] 