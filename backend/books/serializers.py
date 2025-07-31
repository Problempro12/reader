from rest_framework import serializers
from .models import Book, Genre, AgeCategory, Author

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class AgeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeCategory
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.name', read_only=True)
    genre = serializers.CharField(source='genre.name', read_only=True)
    ageCategory = serializers.CharField(source='age_category.name', read_only=True)
    cover = serializers.CharField(source='cover', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'cover', 'genre', 'ageCategory',
            'description', 'is_premium', 'rating', 'litres_rating',
            'series', 'translator', 'technical', 'created_at', 'updated_at'
        ] 