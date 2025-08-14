from django.core.management.base import BaseCommand
from achievements.models import Achievement

class Command(BaseCommand):
    help = 'Обновляет категории достижений на новые значения'

    def handle(self, *args, **options):
        # Маппинг старых значений на новые
        category_mapping = {
            'reading': 'READING',
            'books': 'BOOKS', 
            'social': 'SOCIAL',
            'other': 'OTHER'
        }
        
        updated_count = 0
        
        for old_category, new_category in category_mapping.items():
            achievements = Achievement.objects.filter(category=old_category)
            count = achievements.update(category=new_category)
            if count > 0:
                updated_count += count
                self.stdout.write(
                    self.style.SUCCESS(f'Обновлено {count} достижений с категории {old_category} на {new_category}')
                )
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING('Нет достижений для обновления')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Всего обновлено {updated_count} достижений')
            )