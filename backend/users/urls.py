from django.urls import path
from . import views
from .views import UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('premium/', views.PremiumSubscriptionView.as_view(), name='premium-subscription'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
