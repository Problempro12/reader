from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from yookassa import Configuration, Payment as YooPayment
import uuid
import json

from .models import PremiumPlan, Payment, PaymentWebhook
from .serializers import PremiumPlanSerializer, PaymentSerializer, CreatePaymentSerializer


# Настройка ЮKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


class PremiumPlanListView(generics.ListAPIView):
    """Список доступных тарифных планов"""
    queryset = PremiumPlan.objects.filter(is_active=True)
    serializer_class = PremiumPlanSerializer
    permission_classes = [permissions.AllowAny]


class PaymentListView(generics.ListAPIView):
    """Список платежей пользователя"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class CreatePaymentView(generics.CreateAPIView):
    """Создание платежа"""
    serializer_class = CreatePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        plan = PremiumPlan.objects.get(id=plan_id)
        user = request.user
        
        # Создаем платеж в нашей системе
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=plan.price,
            currency='RUB'
        )
        
        # Создаем платеж в ЮKassa
        try:
            yoo_payment = YooPayment.create({
                "amount": {
                    "value": str(plan.price),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"{settings.FRONTEND_URL}/payments/success/"
                },
                "capture": True,
                "description": f"Премиум подписка: {plan.name}",
                "metadata": {
                    "payment_id": str(payment.id),
                    "user_id": str(user.id),
                    "plan_id": str(plan.id)
                }
            }, idempotency_key=str(payment.id))
            
            # Обновляем наш платеж данными из ЮKassa
            payment.yookassa_payment_id = yoo_payment.id
            payment.payment_url = yoo_payment.confirmation.confirmation_url
            payment.status = yoo_payment.status
            payment.save()
            
            return Response({
                'payment_id': payment.id,
                'payment_url': payment.payment_url,
                'amount': payment.amount,
                'status': payment.status
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            payment.delete()  # Удаляем неудачный платеж
            return Response({
                'error': 'Ошибка создания платежа',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webhook_handler(request):
    """Обработчик webhook уведомлений от ЮKassa"""
    try:
        # Получаем данные из webhook
        event = request.headers.get('X-Event-Name') or request.data.get('event')
        payment_id = request.data.get('object', {}).get('id')
        
        print(f"Webhook received: event={event}, payment_id={payment_id}")
        print(f"Request data: {request.data}")
        print(f"Request headers: {dict(request.headers)}")
        
        if not event or not payment_id:
            return Response({'error': 'Неверные данные webhook'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Сохраняем webhook для отладки
        webhook = PaymentWebhook.objects.create(
            event=event,
            payment_id=payment_id,
            raw_data=request.data
        )
        
        # Обрабатываем только события платежей
        if event == 'payment.succeeded':
            try:
                # Получаем платеж из ЮKassa
                yoo_payment = YooPayment.find_one(payment_id)
                
                # Находим наш платеж
                payment = Payment.objects.get(yookassa_payment_id=payment_id)
                
                # Обновляем статус
                payment.status = yoo_payment.status
                payment.paid_at = timezone.now()
                payment.save()
                
                # Активируем премиум-подписку
                if payment.activate_premium():
                    webhook.processed = True
                    webhook.save()
                    
                    return Response({'status': 'success'}, 
                                  status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Не удалось активировать премиум'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                    
            except Payment.DoesNotExist:
                return Response({'error': 'Платеж не найден'}, 
                              status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': f'Ошибка обработки платежа: {str(e)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif event == 'payment.canceled':
            try:
                payment = Payment.objects.get(yookassa_payment_id=payment_id)
                payment.status = 'canceled'
                payment.save()
                
                webhook.processed = True
                webhook.save()
                
                return Response({'status': 'success'}, 
                              status=status.HTTP_200_OK)
            except Payment.DoesNotExist:
                return Response({'error': 'Платеж не найден'}, 
                              status=status.HTTP_404_NOT_FOUND)
        
        return Response({'status': 'ignored'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': f'Ошибка обработки webhook: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, payment_id):
    """Проверка статуса платежа"""
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        
        # Обновляем статус из ЮKassa
        if payment.yookassa_payment_id:
            try:
                yoo_payment = YooPayment.find_one(payment.yookassa_payment_id)
                payment.status = yoo_payment.status
                if yoo_payment.status == 'succeeded' and not payment.paid_at:
                    payment.paid_at = timezone.now()
                    payment.activate_premium()
                payment.save()
            except Exception as e:
                pass  # Игнорируем ошибки обновления статуса
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
        
    except Payment.DoesNotExist:
        return Response({'error': 'Платеж не найден'}, 
                      status=status.HTTP_404_NOT_FOUND)
