from django.core.management.base import BaseCommand
from payments.models import PremiumPlan


class Command(BaseCommand):
    help = 'Create default premium plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Премиум на месяц',
                'description': 'Получите доступ ко всем премиум-функциям на 30 дней',
                'price': 299.00,
                'duration_days': 30,
                'features': [
                    'Без рекламы',
                    'Приоритетная поддержка',
                    'Эксклюзивные книги',
                    'Расширенная статистика'
                ]
            },
            {
                'name': 'Премиум на 3 месяца',
                'description': 'Получите доступ ко всем премиум-функциям на 90 дней со скидкой',
                'price': 799.00,
                'duration_days': 90,
                'features': [
                    'Без рекламы',
                    'Приоритетная поддержка',
                    'Эксклюзивные книги',
                    'Расширенная статистика',
                    'Скидка 11%'
                ]
            },
            {
                'name': 'Премиум на год',
                'description': 'Получите доступ ко всем премиум-функциям на 365 дней с максимальной скидкой',
                'price': 2999.00,
                'duration_days': 365,
                'features': [
                    'Без рекламы',
                    'Приоритетная поддержка',
                    'Эксклюзивные книги',
                    'Расширенная статистика',
                    'Скидка 17%',
                    'Бонусные функции'
                ]
            }
        ]

        for plan_data in plans_data:
            plan, created = PremiumPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Premium plans seeding completed!')
        )
