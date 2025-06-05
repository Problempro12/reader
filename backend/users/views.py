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

User = get_user_model()

def run_async(coro):
    return asyncio.run(coro)

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
            
            # Используем стандартную функцию authenticate для аутентификации через настроенные бэкенды
            user = authenticate(request, email=serializer.validated_data['email'], password=serializer.validated_data['password']) 
            
            if user is not None:
                print(f"Пользователь аутентифицирован: {user}")
                # Аутентификация успешна, генерируем токены
                refresh = RefreshToken.for_user(user)
                
                # Получаем данные пользователя через сериализатор
                serializer = self.get_serializer(user)
                
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
            user = request.user
            prisma = Prisma()
            await prisma.connect()

            # Получаем статистику по книгам
            user_books = await prisma.userbook.find_many(
                where={
                    'userId': user.id
                }
            )

            # Группируем книги по статусу
            stats = {
                'reading': 0,
                'completed': 0,
                'planned': 0
            }
            
            for book in user_books:
                stats[book.status] += 1

            await prisma.disconnect()
            
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'stats': stats,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            })

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
