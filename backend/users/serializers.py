from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# Добавляем словарь для статистики книг
class BookStatsSerializer(serializers.Serializer):
    read_count = serializers.IntegerField()
    planning_count = serializers.IntegerField()
    reading_count = serializers.IntegerField()
    dropped_count = serializers.IntegerField()
    total_count = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    # stats = BookStatsSerializer(read_only=True, required=False)
    stats = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'is_premium',
            'premium_expiration_date',
            'hide_ads',
            'avatar',
            'about',
            'stats',
            'is_staff',
            'is_superuser',
        )
        read_only_fields = ('email', 'is_premium', 'premium_expiration_date', 'hide_ads', 'is_staff', 'is_superuser')

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'error_messages': {
                    'required': 'Имя пользователя обязательно',
                    'blank': 'Имя пользователя не может быть пустым',
                    'max_length': 'Имя пользователя не может быть длиннее 150 символов'
                }
            },
            'email': {
                'error_messages': {
                    'required': 'Email обязателен',
                    'blank': 'Email не может быть пустым',
                    'invalid': 'Введите корректный email адрес'
                }
            },
            'password': {
                'error_messages': {
                    'required': 'Пароль обязателен',
                    'blank': 'Пароль не может быть пустым',
                    'min_length': 'Пароль должен содержать минимум 8 символов'
                }
            }
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password2': 'Пароли не совпадают'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True) 