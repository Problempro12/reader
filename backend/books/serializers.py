from rest_framework import serializers
from .models import Book, Author, UserBook, ReadingProgress

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model"""
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'photo_url']

class BookSerializer(serializers.ModelSerializer):
    """Serializer for the Book model"""
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        write_only=True
    )
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_id', 'cover_url', 'description', 
                  'content', 'published_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookListSerializer(serializers.ModelSerializer):
    """Serializer for listing books without content"""
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_url', 'description', 'published_date']
        read_only_fields = ['id']

class BookFrontendSerializer(serializers.ModelSerializer):
    """Serializer for frontend compatibility"""
    author = AuthorSerializer(read_only=True)
    cover = serializers.CharField(source='cover_url', read_only=True)
    genre = serializers.SerializerMethodField()
    ageCategory = serializers.SerializerMethodField()
    isPremium = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    vote_count = serializers.IntegerField(read_only=True)
    is_book_of_week = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover', 'genre', 'ageCategory', 
                  'description', 'isPremium', 'rating', 'vote_count', 'is_book_of_week']
    
    def get_genre(self, obj):
        # Возвращаем разные жанры для разнообразия
        genres = [
            "Художественная литература",
            "Фантастика", 
            "Детектив",
            "Роман",
            "Классика",
            "Приключения",
            "Драма",
            "Фэнтези"
        ]
        return genres[obj.id % len(genres)]
    
    def get_ageCategory(self, obj):
        # Возвращаем разные возрастные категории для разнообразия
        age_categories = ["0+", "6+", "12+", "16+", "18+"]
        return age_categories[obj.id % len(age_categories)]
    
    def get_isPremium(self, obj):
        # Возвращаем False по умолчанию, можно добавить поле в модель позже
        return False
    
    def get_rating(self, obj):
        # Вычисляем средний рейтинг на основе пользовательских оценок
        from django.db.models import Avg
        avg_rating = obj.user_books.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0.0

class UserBookSerializer(serializers.ModelSerializer):
    """Serializer for the UserBook model"""
    book = BookListSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )
    
    class Meta:
        model = UserBook
        fields = ['id', 'user', 'book', 'book_id', 'status', 'rating', 'added_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'added_at', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReadingProgressSerializer(serializers.ModelSerializer):
    """Serializer for the ReadingProgress model"""
    progress_percentage = serializers.ReadOnlyField()
    user_book = UserBookSerializer(read_only=True)
    
    class Meta:
        model = ReadingProgress
        fields = ['id', 'user_book', 'position', 'current_page', 'total_pages', 'progress_percentage', 'created_at']
        read_only_fields = ['id', 'progress_percentage', 'created_at']