from rest_framework import serializers

class GenreSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class AgeCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

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