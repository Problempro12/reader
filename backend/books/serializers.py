from rest_framework import serializers
from .models import Book, Genre, AgeCategory

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class AgeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeCategory
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    ageCategory = AgeCategorySerializer()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'coverUrl', 'externalId',
            'rating', 'rating_count', 'author', 'genre', 'ageCategory',
            'isPremium', 'isbn', 'year', 'series', 'translator',
            'volume', 'copyrightHolder'
        ] 