import sys
import os

# Добавляем корневую директорию проекта (содержащую backend) в sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

print("SYS.PATH перед импортом Prisma:", sys.path) # Отладочный вывод

from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from backend.prisma.generated.client import Prisma
from datetime import datetime, timedelta
import asyncio
from django.http import JsonResponse, FileResponse, HttpResponse, Http404
from asgiref.sync import sync_to_async, async_to_sync
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.backends import EmailBackend
from django.conf import settings
import mimetypes

User = get_user_model()

def run_async(coro):
    return asyncio.run(coro)

async def create_prisma_user(user):
    prisma = Prisma()
    await prisma.connect()
    try:
        prisma_user = await prisma.users_user.create(
            data={
                'email': user.email,
                'username': user.username,
                'passwordHash': user.password,
                'isPremium': user.is_premium,
                'isStaff': user.is_staff,
                'isSuperuser': user.is_superuser,
                'registrationDate': user.date_joined
            }
        )
        print(f"Пользователь создан в Prisma: {prisma_user}")
        return prisma_user
    except Exception as e:
        print(f"Ошибка при создании пользователя в Prisma: {str(e)}")
        if "Unique constraint failed on the fields: (`email`)" in str(e):
             print("Ошибка уникальности по email при создании в Prisma")
        elif "Unique constraint failed on the fields: (`username`)" in str(e):
             print("Ошибка уникальности по username при создании в Prisma")
        else:
            pass
        raise e
    finally:
        await prisma.disconnect()

# Новая вьюха для обслуживания медиа-файлов с CORS-заголовками в режиме отладки
def serve_media_with_cors(request, path):
    # Формируем полный путь к файлу в директории MEDIA_ROOT
    # Использование os.path.join безопасно и обрабатывает разделители путей
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    print(f"Attempting to serve media file from: {full_path}") # Отладочный лог

    # Убеждаемся, что файл существует и находится внутри MEDIA_ROOT для безопасности
    if not os.path.exists(full_path) or not full_path.startswith(settings.MEDIA_ROOT):
        print(f"File not found or outside MEDIA_ROOT: {full_path}") # Отладочный лог
        raise Http404('File not found.')

    try:
        # Определяем mime-тип файла
        mime_type, encoding = mimetypes.guess_type(full_path)
        mime_type = mime_type or 'application/octet-stream' # Дефолтный mime-тип, если не определен
        
        # Открываем файл и создаем FileResponse
        # Добавляем заголовки CORS вручную
        response = FileResponse(open(full_path, 'rb'), content_type=mime_type)
        response['Access-Control-Allow-Origin'] = '*' # Или конкретные origin-ы из settings.CORS_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = '*'
        
        print(f"Successfully serving media file: {full_path} with CORS headers") # Отладочный лог
        return response
    except Exception as e:
        print(f"Error serving media file {full_path}: {e}") # Логируем ошибку
        raise Http404('Error serving file.')

# Create your views here.

class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("Получены данные:", request.data)  # Логируем входящие данные
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            print("Ошибки валидации:", serializer.errors)  # Логируем ошибки валидации
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, существует ли пользователь с таким email
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            print("Найден пользователь с email:", serializer.validated_data['email'])  # Логируем найденного пользователя
            return Response(
                {'email': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            pass

        # Проверяем, существует ли пользователь с таким username
        try:
            user = User.objects.get(username=serializer.validated_data['username'])
            print("Найден пользователь с username:", serializer.validated_data['username'])  # Логируем найденного пользователя
            return Response(
                {'username': 'Пользователь с таким именем уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            pass

        # Создаем пользователя
        try:
            user = serializer.save()
            print("Пользователь создан:", user)  # Логируем созданного пользователя
        except Exception as e:
            print("Ошибка при создании пользователя:", str(e))  # Логируем ошибку создания
            return Response(
                {'error': 'Ошибка при создании пользователя'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Создаем пользователя в Prisma
        try:
            asyncio.run(create_prisma_user(user))
            print("Пользователь создан в Prisma")  # Логируем успешное создание в Prisma
        except Exception as e:
            print("Ошибка при создании пользователя в Prisma:", str(e))  # Логируем ошибку Prisma
            return Response(
                {'error': 'Ошибка при создании пользователя. Пожалуйста, попробуйте позже.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print("Получены данные для входа:", request.data)
        try:
            serializer = UserLoginSerializer(data=request.data)
            if not serializer.is_valid():
                print("Ошибки валидации:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            print("Данные валидны, пытаемся аутентифицировать пользователя")
            
            # Используем EmailBackend для аутентификации
            backend = EmailBackend()
            user = backend.authenticate(request, email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            
            if user is not None:
                print(f"Пользователь аутентифицирован: {user}")
                # Аутентификация успешна, генерируем токены
                refresh = RefreshToken.for_user(user)

                # Получаем данные пользователя через сериализатор
                serializer = UserSerializer(user)
                
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data # Сериализованные данные пользователя
                }
                
                print("Отправляем ответ:", response_data)
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                print("Аутентификация не удалась")
                return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("Произошла ошибка:", str(e))
            return Response(
                {'detail': 'Внутренняя ошибка сервера'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        async def get_profile():
            try:
                user = request.user
                print(f"Получение профиля для пользователя: {user.id}")
                print(f"Данные пользователя: {user.__dict__}")
                print(f"Флаги администратора: is_staff={user.is_staff}, is_superuser={user.is_superuser}")

                prisma = Prisma()
                await prisma.connect()
                print("Подключение к Prisma успешно")

                # Получаем статистику по книгам
                try:
                    user_books = await prisma.userbook.find_many(
                        where={
                            'userId': user.id  # Передаем ID как целое число
                        }
                    )
                    print(f"Найдено книг пользователя: {len(user_books)}")
                    print(f"Данные user_books: {user_books}") # Добавлено логирование user_books
                except Exception as e:
                    print(f"Ошибка при получении книг пользователя: {str(e)}")
                    user_books = []

                # Группируем книги по статусу
                stats = {
                    'reading': 0,
                    'completed': 0,
                    'planned': 0
                }

                for book in user_books:
                    if book['status'] == 'READING':
                        stats['reading'] += 1
                    elif book['status'] == 'READ':
                        stats['completed'] += 1
                    elif book['status'] == 'PLANNING':
                        stats['planned'] += 1

                await prisma.disconnect()

                # Сериализуем данные пользователя, передавая контекст запроса
                serializer = UserSerializer(user, context={'request': request})
                data = serializer.data
                data['stats'] = stats
                print(f"Отправляемые данные пользователя: {data}")

                return data
            except Exception as e:
                print(f"Ошибка при получении профиля: {str(e)}")
                raise e

        return Response(run_async(get_profile()))

    def patch(self, request):
        try:
            user = request.user
            print(f"Обновление профиля для пользователя: {user.id}")
            print(f"Полученные данные: {request.data}")
            print(f"Полученные файлы: {request.FILES}")

            # Обновляем данные в Django
            serializer = UserSerializer(user, data=request.data, partial=True)
            if not serializer.is_valid():
                print(f"Ошибки валидации: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Если есть файл аватара, сохраняем его
            if 'avatar' in request.FILES:
                print(f"Получен файл аватара: {request.FILES['avatar']}")
                user.avatar = request.FILES['avatar']

            # Сохраняем пользователя в Django. Это обновит его поля и сохранит файл аватара.
            serializer.save()
            user.refresh_from_db() # Обновляем объект пользователя из базы, чтобы получить актуальный URL аватара

            # Обновляем данные в Prisma с использованием async_to_sync
            # Определяем асинхронную функцию для обновления в Prisma
            async def update_user_in_prisma(user_id, update_data_for_prisma):
                prisma = Prisma()
                await prisma.connect()
                try:
                    # Отладочный вывод: Проверяем, что Prisma Client видит до обновления
                    print(f"Prisma: Пытаемся найти пользователя с ID: {user_id}")
                    # Используем users_user для поиска
                    prisma_user_before_update = await prisma.users_user.find_unique(
                        where={'id': user_id} # ID пользователя из Django
                    )
                    print(f"Prisma: Пытаемся найти пользователя по email: {request.user.email}") # Отладочный вывод
                    prisma_user_by_email = await prisma.users_user.find_unique(
                        where={'email': request.user.email}
                    )
                    print(f"Prisma: Найден пользователь по email до обновления: {prisma_user_by_email}") # Отладочный вывод
                    print(f"Prisma: Найден пользователь до обновления: {prisma_user_before_update}")
                    if prisma_user_before_update:
                        print(f"Prisma: Наличие поля 'avatar' в объекте до обновления: {'avatar' in prisma_user_before_update.__dict__}")
                        if 'avatar' in prisma_user_before_update.__dict__:
                            print(f"Prisma: Тип поля 'avatar' до обновления: {type(prisma_user_before_update.__dict__['avatar'])}")
                            print(f"Prisma: Значение поля 'avatar' до обновления: {prisma_user_before_update.avatar}")

                    if update_data_for_prisma:
                        print(f"Prisma: Данные для обновления: {update_data_for_prisma}")
                        # Используем users_user для обновления
                        await prisma.users_user.update(
                            where={'id': user_id},
                            data=update_data_for_prisma
                        )
                finally:
                    await prisma.disconnect()

            # Собираем все данные для обновления в Prisma из request.data и актуального объекта пользователя Django
            update_data_for_prisma = {}
            if 'username' in request.data:
                update_data_for_prisma['username'] = request.data['username']
            if 'about' in request.data:
                update_data_for_prisma['about'] = request.data['about']

            # Добавляем URL аватара, если он существует после сохранения в Django
            if user.avatar and hasattr(user.avatar, 'url'):
                print(f"URL аватара (для Prisma): {user.avatar.url}")
                update_data_for_prisma['avatar'] = user.avatar.url

            # Добавляем флаги администратора
            update_data_for_prisma['is_staff'] = user.is_staff
            update_data_for_prisma['is_superuser'] = user.is_superuser

            # Вызываем асинхронную функцию через async_to_sync
            # Передаем user.id и собранный словарь данных
            if update_data_for_prisma:
                print(f"Prisma: Данные для обновления: {update_data_for_prisma}")
                async_to_sync(update_user_in_prisma)(int(user.id), update_data_for_prisma)

            # Получаем обновленные данные пользователя Django для ответа
            # Повторно сериализуем пользователя, чтобы получить все актуальные поля, включая аватар
            updated_user_serializer = UserSerializer(user)

            return Response(updated_user_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Ошибка при обновлении профиля: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        async def get_notifications():
            prisma = Prisma()
            await prisma.connect()
            notifications = await prisma.notification.find_many(
                where={'userId': self.request.user.id}
            )
            await prisma.disconnect()
            return notifications
        return run_async(get_notifications())

class PremiumSubscriptionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        async def activate_premium():
            prisma = Prisma()
            await prisma.connect()
            
            user = await prisma.users_user.update(
                where={'id': int(self.request.user.id)},
                data={
                    'is_premium': True,
                    'premium_expiration_date': serializer.validated_data.get('expiration_date')
                }
            )
            
            await prisma.notification.create(
                data={
                    'userId': self.request.user.id,
                    'message': 'Премиум подписка успешно активирована!'
                }
            )
            
            await prisma.disconnect()
            return user
        return run_async(activate_premium())
