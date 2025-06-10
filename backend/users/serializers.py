from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.conf import settings # Импортируем настройки Django

User = get_user_model()

# Добавляем словарь для статистики книг
class BookStatsSerializer(serializers.Serializer):
    read_count = serializers.IntegerField()
    planning_count = serializers.IntegerField()
    reading_count = serializers.IntegerField()
    dropped_count = serializers.IntegerField()
    total_count = serializers.IntegerField()

class UserSerializer(serializers.ModelSerializer):
    stats = serializers.JSONField(read_only=True)
    # Заменяем ImageField на SerializerMethodField для правильного формирования URL
    avatar_url = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'is_premium',
            'premium_expiration_date',
            'hide_ads',
            # Заменяем 'avatar' на 'avatar_url'
            'avatar_url',
            'about',
            'stats',
            'is_staff',
            'is_superuser',
        )
        read_only_fields = ('email', 'is_premium', 'premium_expiration_date', 'hide_ads', 'is_staff', 'is_superuser')

    def get_avatar_url(self, obj):
        # obj - это экземпляр модели User
        if obj.avatar:
            # obj.avatar.url возвращает путь относительно MEDIA_URL (например, /media/avatars/...). 
            # Нам нужно сформировать полный URL, включая схему и домен.
            # Убедимся, что не дублируем MEDIA_URL, если он уже в начале пути
            avatar_path = obj.avatar.url
            # Убираем потенциальное дублирование MEDIA_URL в начале пути, если оно есть
            if settings.MEDIA_URL and avatar_path.startswith(settings.MEDIA_URL):
                 # Проверяем, есть ли дублирование, например /media/media/... перед удалением
                 # Если MEDIA_URL=/media/, а avatar_path=/media/media/..., то удаляем одно /media/ 
                 # Более надежный способ - просто использовать path_info и MEDIA_URL
                 avatar_path_without_media_prefix = obj.avatar.name # Получаем путь относительно MEDIA_ROOT
                 print(f"Avatar path without media prefix: {avatar_path_without_media_prefix}") # Лог для отладки
                 full_url_path = f"{settings.MEDIA_URL}{avatar_path_without_media_prefix}"
                 # Убираем двойные слэши, кроме тех, что после схемы
                 full_url_path = full_url_path.replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')

            else:
                # Если MEDIA_URL отсутствует или путь аватара не начинается с него
                avatar_path_without_media_prefix = obj.avatar.name
                full_url_path = f"{settings.MEDIA_URL}{avatar_path_without_media_prefix}"
                full_url_path = full_url_path.replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')

            # Получаем базовый URL из контекста запроса
            # Проверяем, что context и request существуют и доступны
            if 'request' in self.context and self.context['request']:
                request = self.context['request']
                base_url = request.build_absolute_uri('/').rstrip('/')
                # Убираем потенциальный дублирующийся слэш между base_url и full_url_path
                if full_url_path.startswith('/'):
                     return f"{base_url}{full_url_path}"
                else:
                     return f"{base_url}/{full_url_path}"
            else:
                # Если контекст запроса недоступен, возвращаем только относительный путь (менее предпочтительно)
                print("Request context not available in serializer.")
                return full_url_path
        return None # Если аватара нет, возвращаем None

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