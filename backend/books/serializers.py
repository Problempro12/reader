from rest_framework import serializers
<<<<<<< HEAD
from .models import Book, Genre, AgeCategory, Author
=======

class GenreSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c

class AgeCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

<<<<<<< HEAD
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
=======
class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    author = AuthorSerializer()
    description = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    coverUrl = serializers.CharField(source='cover_url', allow_null=True, allow_blank=True, required=False)
    genre = GenreSerializer()
    ageCategory = AgeCategorySerializer()
    rating = serializers.FloatField()
    rating_count = serializers.IntegerField(required=False)
    isPremium = serializers.BooleanField()
    litresRating = serializers.FloatField(source='litres_rating', allow_null=True, required=False)
    litresRatingCount = serializers.IntegerField(source='litres_rating_count', allow_null=True, required=False)
    series = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    translator = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    volume = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    year = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    isbn = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    copyrightHolder = serializers.CharField(source='copyright_holder', allow_null=True, allow_blank=True, required=False)
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at') 
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c
