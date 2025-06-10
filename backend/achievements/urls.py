from django.urls import path
from . import views

app_name = 'achievements'

urlpatterns = [
    path('', views.AchievementListView.as_view(), name='achievement-list'),
    path('my/', views.UserAchievementListView.as_view(), name='user-achievement-list'),
] 