from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PremiumPlanListView.as_view(), name='premium-plans'),
    path('create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('list/', views.PaymentListView.as_view(), name='payment-list'),
    path('status/<uuid:payment_id>/', views.payment_status, name='payment-status'),
    path('webhook/', views.webhook_handler, name='payment-webhook'),
]
