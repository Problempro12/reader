from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class PremiumPlan(models.Model):
    """Модель тарифного плана премиум-подписки"""
    name = models.CharField(max_length=100, verbose_name="Название плана")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration_days = models.IntegerField(verbose_name="Длительность в днях")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    features = models.JSONField(default=list, verbose_name="Особенности")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price}₽"


class Payment(models.Model):
    """Модель платежа"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('waiting_for_capture', 'Ожидает подтверждения'),
        ('succeeded', 'Успешно'),
        ('canceled', 'Отменен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PremiumPlan, on_delete=models.CASCADE, related_name='payments')
    yookassa_payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платеж {self.id} - {self.user.username} - {self.amount}₽"
    
    def is_successful(self):
        return self.status == 'succeeded'
    
    def activate_premium(self):
        """Активирует премиум-подписку для пользователя"""
        if self.is_successful():
            # Если у пользователя уже есть премиум, продлеваем
            if self.user.is_premium and self.user.premium_expiration_date:
                if self.user.premium_expiration_date > timezone.now():
                    # Продлеваем с текущей даты окончания
                    self.user.premium_expiration_date += timedelta(days=self.plan.duration_days)
                else:
                    # Начинаем с текущей даты
                    self.user.premium_expiration_date = timezone.now() + timedelta(days=self.plan.duration_days)
            else:
                # Начинаем с текущей даты
                self.user.premium_expiration_date = timezone.now() + timedelta(days=self.plan.duration_days)
            
            self.user.is_premium = True
            self.user.hide_ads = True
            self.user.save()
            return True
        return False


class PaymentWebhook(models.Model):
    """Модель для хранения webhook уведомлений от ЮKassa"""
    event = models.CharField(max_length=50)
    payment_id = models.CharField(max_length=100)
    raw_data = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Webhook уведомление"
        verbose_name_plural = "Webhook уведомления"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook {self.event} - {self.payment_id}"
