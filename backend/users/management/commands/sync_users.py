from django.core.management.base import BaseCommand
from users.signals import sync_all_users

class Command(BaseCommand):
    help = 'Синхронизирует пользователей Django с Prisma'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем синхронизацию пользователей...')
        sync_all_users()
        self.stdout.write(self.style.SUCCESS('Синхронизация завершена!')) 