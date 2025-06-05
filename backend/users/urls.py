from django.urls import path
from . import views
from .views import UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('premium/', views.PremiumSubscriptionView.as_view(), name='premium-subscription'),
] 