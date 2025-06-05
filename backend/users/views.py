from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from prisma import Prisma
from datetime import datetime, timedelta
import asyncio
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.backends import EmailBackend

User = get_user_model()

def run_async(coro):
    return asyncio.run(coro)

async def create_prisma_user(user):
    prisma = Prisma()
    await prisma.connect()
    try:
        prisma_user = await prisma.user.create(
            data={
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'is_premium': False,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        )
        print(f"Пользователь создан в Prisma: {prisma_user}")
        return prisma_user
    except Exception as e:
        print(f"Ошибка при создании пользователя в Prisma: {str(e)}")
        raise e
    finally:
        await prisma.disconnect()

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
            # Если не удалось создать пользователя в Prisma, удаляем его из Django
            user.delete()
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
                    # Убедитесь, что поле 'status' существует и имеет ожидаемые значения
                    if hasattr(book, 'status') and book.status in stats:
                        stats[book.status] += 1
                    else:
                         print(f"Предупреждение: Неожиданный статус книги или отсутствует поле 'status': {book}")


                print(f"Рассчитанная статистика: {stats}") # Добавлено логирование stats

                await prisma.disconnect()
                print("Отключение от Prisma успешно")

                response_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'stats': stats,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
                print("Данные профиля:", response_data)

                return Response(response_data)
            except Exception as e:
                print(f"Ошибка при получении профиля: {str(e)}")
                if 'prisma' in locals():
                    await prisma.disconnect()
                return Response(
                    {'error': f'Ошибка при получении профиля: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return run_async(get_profile())

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
            
            user = await prisma.user.update(
                where={'id': self.request.user.id},
                data={
                    'is_premium': True,
                    'premium_expiration_date': serializer.validated_data.get('expiration_date')
                }
            )
            
            await prisma.notification.create(
                data={
                    'userId': self.request.user.id,
                    'type': 'PREMIUM_ACTIVATED',
                    'message': 'Премиум подписка успешно активирована!'
                }
            )
            
            await prisma.disconnect()
            return user
        return run_async(activate_premium())
