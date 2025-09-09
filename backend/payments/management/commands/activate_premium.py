from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from payments.models import Payment, PremiumPlan
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Manually activate premium for a user (for testing)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to activate premium for')
        parser.add_argument('--plan', type=int, default=1, help='Plan ID to activate (default: 1)')
        parser.add_argument('--days', type=int, help='Override duration in days')

    def handle(self, *args, **options):
        username = options['username']
        plan_id = options['plan']
        days = options['days']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )
            return

        try:
            plan = PremiumPlan.objects.get(id=plan_id)
        except PremiumPlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Plan with ID {plan_id} not found')
            )
            return

        # Create a test payment
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=plan.price,
            currency='RUB',
            status='succeeded',
            paid_at=timezone.now()
        )

        # Activate premium
        duration_days = days or plan.duration_days
        
        if user.is_premium and user.premium_expiration_date:
            if user.premium_expiration_date > timezone.now():
                # Extend existing premium
                user.premium_expiration_date += timedelta(days=duration_days)
            else:
                # Start from now
                user.premium_expiration_date = timezone.now() + timedelta(days=duration_days)
        else:
            # Start from now
            user.premium_expiration_date = timezone.now() + timedelta(days=duration_days)

        user.is_premium = True
        user.hide_ads = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Premium activated for {username} until {user.premium_expiration_date}'
            )
        )
