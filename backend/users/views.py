from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from prisma import Prisma
from datetime import datetime, timedelta
import asyncio
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        async def login_user_async():
            user = await sync_to_async(authenticate)(
                request=request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            if user is None:
                # Если authenticate вернул None, значит учетные данные неверны
                return Response(
                    {'detail': 'Неверные учетные данные'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Если пользователь найден и аутентифицирован, генерируем или получаем токен
            # Оборачиваем операцию с менеджером в sync_to_async
            token, _ = await sync_to_async(lambda: Token.objects.get_or_create(user=user), thread_sensitive=True)()
            
            # Так как мы получили Django User, используем его напрямую
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        return run_async(login_user_async())

class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Make initial method synchronous
    def initial(self, request, *args, **kwargs):
        # Call the parent initial method synchronously
        super().initial(request, *args, **kwargs)

    # Make get method synchronous
    def get(self, request):
        # Accessing request.user is fine in a sync view
        user = request.user

        # Call async method using run_async wrapper
        stats = run_async(self.get_book_stats(user)) # Uncomment when Prisma is ready

        serializer = UserSerializer(user) # Pass user instance to serializer
        serializer.data['stats'] = stats # Add stats to data manually if not included in serializer directly

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Keep get_book_stats as async because it uses Prisma
    async def get_book_stats(self, user):
        # This method should interact with Prisma to get book stats
        # Example (requires UserBook model and Prisma setup):
        prisma = Prisma()
        await prisma.connect()
        try:
            read_count = await prisma.userbook.count(where={'userId': user.id, 'status': 'READ'})
            planning_count = await prisma.userbook.count(where={'userId': user.id, 'status': 'PLANNING'})
            reading_count = await prisma.userbook.count(where={'userId': user.id, 'status': 'READING'})
            dropped_count = await prisma.userbook.count(where={'userId': user.id, 'status': 'DROPPED'})
            total_count = await prisma.userbook.count(where={'userId': user.id})

            stats = {
                'read_count': read_count,
                'planning_count': planning_count,
                'reading_count': reading_count,
                'dropped_count': dropped_count,
                'total_count': total_count,
            }
            return stats
        finally:
            if prisma.is_connected():
                await prisma.disconnect()

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
