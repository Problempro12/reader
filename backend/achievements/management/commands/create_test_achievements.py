from django.core.management.base import BaseCommand
from achievements.models import Achievement

class Command(BaseCommand):
    help = 'Создает тестовые достижения'

    def handle(self, *args, **options):
        achievements_data = [
            {
                'title': 'Первые шаги',
                'description': 'Прочитайте свою первую книгу',
                'category': Achievement.Category.READING,
                'points': 10,
                'requirement': {'books_read': 1}
            },
            {
                'title': 'Книжный червь',
                'description': 'Прочитайте 5 книг',
                'category': Achievement.Category.READING,
                'points': 25,
                'requirement': {'books_read': 5}
            },
            {
                'title': 'Библиофил',
                'description': 'Прочитайте 10 книг',
                'category': Achievement.Category.READING,
                'points': 50,
                'requirement': {'books_read': 10}
            },
            {
                'title': 'Активный читатель',
                'description': 'Сделайте 10 отметок прогресса',
                'category': Achievement.Category.READING,
                'points': 15,
                'requirement': {'progress_marks': 10}
            },
            {
                'title': 'Марафонец',
                'description': 'Сделайте 50 отметок прогресса',
                'category': Achievement.Category.READING,
                'points': 30,
                'requirement': {'progress_marks': 50}
            },
            {
                'title': 'Критик',
                'description': 'Оцените 5 книг',
                'category': Achievement.Category.SOCIAL,
                'points': 20,
                'requirement': {'books_rated': 5}
            },
            {
                'title': 'Коллекционер',
                'description': 'Добавьте 20 книг в свою библиотеку',
                'category': Achievement.Category.BOOKS,
                'points': 25,
                'requirement': {'books_in_library': 20}
            },
            {
                'title': 'Исследователь',
                'description': 'Прочитайте книги из 3 разных жанров',
                'category': Achievement.Category.READING,
                'points': 35,
                'requirement': {'genres_read': 3}
            },
            {
                'title': 'Постоянный читатель',
                'description': 'Читайте 7 дней подряд',
                'category': Achievement.Category.READING,
                'points': 40,
                'requirement': {'consecutive_days': 7}
            },
            {
                'title': 'Ночной читатель',
                'description': 'Сделайте отметку прогресса после 23:00',
                'category': Achievement.Category.OTHER,
                'points': 15,
                'requirement': {'night_reading': 1}
            }
        ]

        created_count = 0
        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                title=achievement_data['title'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создано достижение: {achievement.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Достижение уже существует: {achievement.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} новых достижений')
        )