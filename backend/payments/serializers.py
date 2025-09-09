from rest_framework import serializers
from .models import PremiumPlan, Payment
from users.serializers import UserSerializer


class PremiumPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days', 'features']


class PaymentSerializer(serializers.ModelSerializer):
    plan = PremiumPlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'plan', 'amount', 'currency', 'status', 
            'payment_url', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'paid_at']


class CreatePaymentSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    
    def validate_plan_id(self, value):
        try:
            plan = PremiumPlan.objects.get(id=value, is_active=True)
            return value
        except PremiumPlan.DoesNotExist:
            raise serializers.ValidationError("Неверный тарифный план")
