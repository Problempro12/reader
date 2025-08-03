from rest_framework import status, viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .serializers import UserSerializer, UserCreateSerializer, BookStatsSerializer
from books.models import UserBook

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """View for user profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        
        # Calculate book statistics
        stats = {
            'read_count': UserBook.objects.filter(user=user, status=UserBook.Status.COMPLETED).count(),
            'planning_count': UserBook.objects.filter(user=user, status=UserBook.Status.PLANNED).count(),
            'reading_count': UserBook.objects.filter(user=user, status=UserBook.Status.READING).count(),
            'dropped_count': UserBook.objects.filter(user=user, status=UserBook.Status.DROPPED).count(),
        }
        stats['total_count'] = stats['read_count'] + stats['planning_count'] + stats['reading_count'] + stats['dropped_count']
        
        # Attach stats to user object
        user.stats = stats
        return user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Recalculate stats after update
        instance = self.get_object()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserBooksView(generics.ListAPIView):
    """View for user's books"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Импортируем здесь, чтобы избежать циклического импорта
        from books.serializers import UserBookSerializer
        return UserBookSerializer
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        
        queryset = UserBook.objects.filter(user=user)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.select_related('book', 'book__author').order_by('-added_at')
