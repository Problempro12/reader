import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from users.models import User
from books.models import Book, Author, UserBook, ReadingProgress

def populate_user_data():
    try:
        user = User.objects.get(email='i@kpit.pw')
        print(f"Найден пользователь: {user.username}")

        # Создаем или получаем авторов
        author1, _ = Author.objects.get_or_create(name='Лев Толстой', defaults={'bio': 'Русский писатель, один из величайших писателей-романистов мира.'})
        author2, _ = Author.objects.get_or_create(name='Федор Достоевский', defaults={'bio': 'Русский писатель, мыслитель, философ и публицист.'})
        author3, _ = Author.objects.get_or_create(name='Михаил Булгаков', defaults={'bio': 'Русский советский писатель, драматург, театральный режиссёр и актёр.'})

        # Создаем или получаем книги
        book1, _ = Book.objects.get_or_create(
            title='Война и мир',
            author=author1,
            defaults={
                'cover_url': 'https://spbcult.ru/upload/iblock/f3e/287cclmhcmxz249sxui2ocmfpxrxmw7l.jpeg',
                'description': 'Эпический роман Льва Толстого о русской жизни в период наполеоновских войн.',
                'content': 'Содержание книги Война и мир...', # Замените на реальное содержание
                'genre': 'Исторический роман',
                'published_date': '1869-01-01'
            }
        )
        book2, _ = Book.objects.get_or_create(
            title='Преступление и наказание',
            author=author2,
            defaults={
                'cover_url': 'https://imo10.labirint.ru/books/1003201/cover.jpg/363-0',
                'description': 'Психологический роман Федора Достоевского о студенте, совершившем убийство.',
                'content': 'Содержание книги Преступление и наказание...', # Замените на реальное содержание
                'genre': 'Философский роман',
                'published_date': '1866-01-01'
            }
        )
        book3, _ = Book.objects.get_or_create(
            title='Мастер и Маргарита',
            author=author3,
            defaults={
                'cover_url': 'https://cdn.ast.ru/v2/ASE000000000702015/COVER/cover1__w220.jpg',
                'description': 'Фантастический роман Михаила Булгакова, сочетающий сатиру, мистику и философию.',
                'content': 'Содержание книги Мастер и Маргарита...', # Замените на реальное содержание
                'genre': 'Фантастика',
                'published_date': '1967-01-01'
            }
        )
        book4, _ = Book.objects.get_or_create(
            title='Анна Каренина',
            author=author1,
            defaults={
                'cover_url': 'https://cdn.ast.ru/v2/ASE000000000720964/COVER/cover1__w220.jpg',
                'description': 'Роман Льва Толстого о трагической любви и общественной морали.',
                'content': 'Содержание книги Анна Каренина...', # Замените на реальное содержание
                'genre': 'Роман',
                'published_date': '1877-01-01'
            }
        )

        # Добавляем книги пользователю и устанавливаем прогресс

        # Книга 1: Прочитана
        user_book1, created = UserBook.objects.get_or_create(
            user=user, book=book1,
            defaults={'status': UserBook.Status.COMPLETED, 'rating': 5}
        )
        if created:
            print(f"Добавлена книга '{book1.title}' со статусом 'Прочитано'.")

        # Книга 2: В процессе чтения
        user_book2, created = UserBook.objects.get_or_create(
            user=user, book=book2,
            defaults={'status': UserBook.Status.READING, 'rating': None}
        )
        if created:
            print(f"Добавлена книга '{book2.title}' со статусом 'В процессе чтения'.")
        
        # Добавляем прогресс для книги в процессе чтения
        # Создаем 50 записей ReadingProgress (в 10 раз больше)
        total_pages_book2 = 300
        for i in range(1, 51):
            current_page = min(i * 6, total_pages_book2)  # Увеличиваем на 6 страниц за раз (300/50)
            position = i * 600  # Увеличиваем позицию
            ReadingProgress.objects.create(
                user_book=user_book2,
                current_page=current_page,
                position=position,
                total_pages=total_pages_book2
            )
            print(f"Добавлен прогресс для книги '{book2.title}': страница {current_page}, позиция {position}")

        # Книга 3: Запланирована
        user_book3, created = UserBook.objects.get_or_create(
            user=user, book=book3,
            defaults={'status': UserBook.Status.PLANNED, 'rating': None}
        )
        if created:
            print(f"Добавлена книга '{book3.title}' со статусом 'Запланировано'.")

        # Книга 4: Прочитана с оценкой
        user_book4, created = UserBook.objects.get_or_create(
            user=user, book=book4,
            defaults={'status': UserBook.Status.COMPLETED, 'rating': 4}
        )
        if created:
            print(f"Добавлена книга '{book4.title}' со статусом 'Прочитано'.")

        print("Данные пользователя успешно заполнены.")

    except User.DoesNotExist:
        print("Ошибка: Пользователь с email 'i@kpit.pw' не найден. Пожалуйста, убедитесь, что пользователь существует.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    populate_user_data()