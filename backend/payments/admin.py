from django.contrib import admin
from .models import PremiumPlan, Payment, PaymentWebhook


@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['price']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'amount', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at', 'plan']
    search_fields = ['user__username', 'user__email', 'yookassa_payment_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'paid_at']
    ordering = ['-created_at']


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ['event', 'payment_id', 'processed', 'created_at']
    list_filter = ['event', 'processed', 'created_at']
    search_fields = ['payment_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
