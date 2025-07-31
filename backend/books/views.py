from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Book, Genre, AgeCategory, Author
from .serializers import BookSerializer, GenreSerializer, AgeCategorySerializer
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from .google_books_api import GoogleBooksAPI
import asyncio
<<<<<<< HEAD
=======
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from bs4 import BeautifulSoup
from asgiref.sync import async_to_sync, sync_to_async
from scripts.import_books import import_books
from django.utils.decorators import classonlymethod

def run_async(coro):
    return asyncio.run(coro)

async def check_and_award_achievements(user_id: int, prisma: Prisma):
    """Проверяет и выдает достижения, связанные с голосованием."""
    all_voting_achievements = await prisma.achievement.find_many(
        where={'type': 'voting'}
    )

    for achievement in all_voting_achievements:
        criteria = achievement.criteria
        if 'min_votes' in criteria:
            # Проверяем количество голосов пользователя
            user_votes_count = await prisma.vote.count(
                where={'userId': user_id}
            )
            if user_votes_count >= criteria['min_votes']:
                # Проверяем, получено ли уже это достижение пользователем
                existing_user_achievement = await prisma.userachievement.find_first(
                    where={
                        'userId': user_id,
                        'achievementId': achievement.id
                    }
                )
                if not existing_user_achievement:
                    # Выдаем достижение
                    await prisma.userachievement.create(
                        data={
                            'userId': user_id,
                            'achievementId': achievement.id
                        }
                    )
                    print(f"Достижение '{achievement.name}' выдано пользователю {user_id}")

# Create your views here.
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c

class BookListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer
<<<<<<< HEAD
    queryset = Book.objects.all()
=======

    def get_queryset(self):
        async def get_books():
            prisma = Prisma()
            await prisma.connect()
            # Проверяем включение связанных моделей
            books = await prisma.book.find_many(
                include={
                    'author': True,
                    'genre': True,
                    'ageCategory': True
                }
            )
            await prisma.disconnect()
            return books
        return run_async(get_books())

    def perform_create(self, serializer):
        async def create_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.create(data=serializer.validated_data)
            await prisma.disconnect()
            return book
        return run_async(create_book())
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

class GenreListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

class AgeCategoryListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgeCategorySerializer
    queryset = AgeCategory.objects.all()

class ImportBooksView(APIView):
    def post(self, request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.import_books())
        return Response({'result': result})

    async def import_books(self):
        api = GoogleBooksAPI()
        CATEGORIES = ['fiction', 'fantasy', 'science fiction', 'mystery', 'romance']
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        for category in CATEGORIES:
            books = await api.search_books(f"subject:{category}", max_results=10)
            for google_book in books:
                try:
                    book_data = await api.get_book_details(google_book.get('id'))
                    if not book_data:
                        continue
                    volume_info = book_data.get('volumeInfo', {})
                    title = volume_info.get('title')
                    authors = volume_info.get('authors', [])
                    categories = volume_info.get('categories', [])
                    if not title or not authors:
                        continue
                    author_name = authors[0]
                    author, _ = Author.objects.get_or_create(name=author_name)
                    genre_name = categories[0] if categories else 'Художественная литература'
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    age_category, _ = AgeCategory.objects.get_or_create(name='Для взрослых')
                    # Проверка на существование книги
                    if Book.objects.filter(title=title, author=author).exists():
                        total_skipped += 1
                        continue
                    cover = volume_info.get('imageLinks', {}).get('thumbnail', '')
                    description = volume_info.get('description', '')
                    Book.objects.create(
                        title=title,
                        author=author,
                        cover=cover,
                        description=description,
                        genre=genre,
                        age_category=age_category,
                        is_premium=False,
                        rating=volume_info.get('averageRating', 0.0),
                        series=volume_info.get('series', ''),
                        translator=volume_info.get('translator', ''),
                    )
                    total_imported += 1
                except Exception as e:
                    total_errors += 1
                    continue
        return {
            'imported': total_imported,
            'skipped': total_skipped,
            'errors': total_errors
        }

<<<<<<< HEAD
# Добавь остальные вьюхи по аналогии, если нужно (UserBook, Vote, ReadingProgress и т.д.)
=======
            await prisma.disconnect()
            return vote
        return async_to_sync(create_vote())

class ProgressCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        async def create_progress():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            progress = await prisma.readingprogress.create(
                data={
                    'userId': self.request.user.id,
                    'bookId': serializer.validated_data['bookId'],
                    'weekNumber': current_week,
                    'marks': serializer.validated_data.get('marks', 1),
                }
            )
            await prisma.disconnect()
            return progress
        return run_async(create_progress())

class WeeklyResultListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        async def get_results():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            results = await prisma.weeklyresult.find_many(
                where={'weekNumber': current_week},
                include={
                    'genre': True,
                    'ageCategory': True,
                    'book': True,
                    'leader': True,
                }
            )
            await prisma.disconnect()
            return results
        return run_async(get_results())

class ScrapeLitresView(APIView):
    permission_classes = [IsAuthenticated]

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view.view_is_async = True
        return view

    async def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = await sync_to_async(self.initialize_request)(request)
        self.request = request
        self.headers = self.default_response_headers

        try:
            await sync_to_async(self.perform_authentication)(request)
            await sync_to_async(self.check_permissions)(request)
            await sync_to_async(self.check_throttles)(request)

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            
            response = await handler(request, *args, **kwargs)

        except Exception as exc:
            response = await sync_to_async(self.handle_exception)(exc)

        self.response = response
        return response

    async def post(self, request):
        """Получение информации о книге с Litres по URL"""
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL не указан'}, status=400)

        try:
            print(f"Начинаем запрос к Litres: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            print("Отправляем запрос с заголовками:", headers)
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Получен ответ. Статус: {response.status_code}")
            print(f"Заголовки ответа: {response.headers}")
            print(f"Содержимое ответа: {response.text[:1000]}...")  # Выводим первые 1000 символов
            response.raise_for_status()
            print("Начинаем парсинг HTML")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Проверяем все возможные селекторы для заголовка
            title_selectors = [
                'h1.biblio_book_name',
                'h1[itemprop="name"]',
                '.biblio_book_name',
                'h1'
            ]

            title = None
            for selector in title_selectors:
                title = soup.select_one(selector)
                if title:
                    print(f"Найден заголовок с селектором {selector}")
                    break

            if not title:
                print("Не найден заголовок книги")
                print("Доступные h1:", [h1.text for h1 in soup.find_all('h1')])
                return Response({'error': 'Не удалось найти информацию о книге'}, status=400)
            title = title.text.strip()
            print(f"Найден заголовок: {title}")

            # Ищем автора в новой структуре
            author = soup.select_one('div.BookDetailsHeader-module__CvBt5W__persons a[data-testid="art__personName--link"] span[itemprop="name"]')
            if not author:
                print("Не найден автор")
                print("Доступные элементы с автором:", [a.text for a in soup.find_all('a', attrs={'data-testid': 'art__personName--link'})])
                return Response({'error': 'Не удалось найти информацию об авторе'}, status=400)
            author = author.text.strip()
            print(f"Найден автор: {author}")

            # Ищем описание
            description = soup.select_one('div[itemprop="description"] div.text-html')
            if description:
                description = description.text.strip()
            else:
                description = ''
            print(f"Найдено описание: {description[:100]}...")

            # Ищем URL обложки
            cover_img = soup.select_one('img[itemprop="image"]')
            cover_url = cover_img['src'] if cover_img else ''
            print(f"Найден URL обложки: {cover_url}")

            # Ищем жанры (категории)
            categories = [a.text.strip() for a in soup.select('a[data-qa="genre-item-link"]')]
            if not categories:
                categories = [a.text.strip() for a in soup.select('a.biblio_book_info_genre')]
            print(f"Найдены категории: {categories}")
            
            # Ищем ISBN
            isbn_element = soup.find(lambda tag: tag.name == "div" and "ISBN:" in tag.text)
            isbn = isbn_element.text.replace("ISBN:", "").strip() if isbn_element else ""
            print(f"Найден ISBN: {isbn}")

            book_data = {
                'title': title,
                'authorId': author,
                'description': description,
                'coverUrl': cover_url,
                'genreId': categories[0] if categories else None,
                'ageCategoryId': categories[1] if len(categories) > 1 else None,
                'isPremium': False,
                'litresRating': 0,
                'litresRatingCount': 0,
                'series': '',
                'translator': '',
                'volume': '',
                'year': '',
                'isbn': isbn,
                'copyrightHolder': '',
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            }

            return Response(book_data, status=200)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к Litres: {e}")
            return Response({'error': f'Ошибка при подключении к Litres: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return Response({'error': f'Неожиданная ошибка при парсинге Litres: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RunImportBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            async_to_sync(import_books)()
            return Response({'message': 'Импорт книг успешно запущен.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Ошибка при запуске импорта: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrentWeekBookView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        async def get_current_book():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            result = await prisma.weeklyresult.find_first(
                where={'weekNumber': current_week},
                include={
                    'book': {
                        'include': {
                            'genre': True,
                            'ageCategory': True
                        }
                    }
                }
            )
            await prisma.disconnect()
            return result.book if result else None
        return run_async(get_current_book())

class VotingCandidatesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        async def get_candidates():
            prisma = Prisma()
            await prisma.connect()
            
            # Получаем 10 книг с наивысшим рейтингом
            candidates = await prisma.book.find_many(
                take=10,
                order={
                    'rating': 'desc'
                },
                include={
                    'genre': True,
                    'ageCategory': True
                }
            )
            
            # Получаем текущую неделю
            current_week = datetime.now().isocalendar()[1]
            
            # Получаем книги, за которые пользователь уже голосовал
            user_votes = await prisma.vote.find_many(
                where={
                    'userId': self.request.user.id,
                    'weekNumber': current_week
                }
            )
            voted_book_ids = [vote.bookId for vote in user_votes]
            
            # Фильтруем книги, за которые пользователь еще не голосовал
            candidates = [book for book in candidates if book.id not in voted_book_ids]
            
            await prisma.disconnect()
            return candidates
        return run_async(get_candidates())

class UserVotesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        async def get_user_votes():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            votes = await prisma.vote.find_many(
                where={
                    'userId': self.request.user.id,
                    'weekNumber': current_week
                }
            )
            await prisma.disconnect()
            return votes
        return run_async(get_user_votes())

class ProgressDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        async def get_progress():
            prisma = Prisma()
            await prisma.connect()
            
            book_id = self.kwargs['pk']
            current_week = datetime.now().isocalendar()[1]
            
            # Получаем отметки пользователя
            user_progress = await prisma.readingprogress.find_first(
                where={
                    'userId': self.request.user.id,
                    'bookId': book_id,
                    'weekNumber': current_week
                }
            )
            
            # Получаем общее количество отметок
            total_progress = await prisma.readingprogress.find_many(
                where={
                    'bookId': book_id,
                    'weekNumber': current_week
                }
            )
            
            total_marks = sum(progress.marks for progress in total_progress)
            user_marks = user_progress.marks if user_progress else 0
            
            await prisma.disconnect()
            
            return {
                'userMarks': user_marks,
                'totalMarks': total_marks
            }
        return run_async(get_progress())

class BookRatingView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    async def get_rating(self, request, pk):
        prisma = Prisma()
        await prisma.connect()

        try:
            # Получаем рейтинг пользователя
            user_rating = await prisma.userbook.find_first(
                where={
                    'userId': request.user.id,
                    'bookId': pk
                },
                select={
                    'rating': True
                }
            )

            # Получаем средний рейтинг книги
            book = await prisma.book.find_unique(
                where={'id': pk},
                select={
                    'rating': True,
                    'rating_count': True
                }
            )

            return Response({
                'user_rating': user_rating.rating if user_rating else None,
                'average_rating': book.rating if book else 0,
                'rating_count': book.rating_count if book else 0
            })
        finally:
            await prisma.disconnect()

class BookRateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    async def create_rating(self, request, pk):
        rating = request.data.get('rating')
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response(
                {'error': 'Необходимо указать рейтинг от 1 до 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prisma = Prisma()
        await prisma.connect()

        try:
            # Создаем или обновляем рейтинг пользователя
            user_book = await prisma.userbook.upsert(
                where={
                    'userId_bookId': {
                        'userId': request.user.id,
                        'bookId': pk
                    }
                },
                data={
                    'create': {
                        'userId': request.user.id,
                        'bookId': pk,
                        'status': 'READ',
                        'rating': rating
                    },
                    'update': {
                        'rating': rating
                    }
                }
            )

            # Пересчитываем средний рейтинг книги
            ratings = await prisma.userbook.find_many(
                where={
                    'bookId': pk,
                    'rating': {'not': None}
                },
                select={'rating': True}
            )

            if ratings:
                total_rating = sum(r.rating for r in ratings)
                average_rating = total_rating / len(ratings)
                rating_count = len(ratings)

                await prisma.book.update(
                    where={'id': pk},
                    data={
                        'rating': average_rating,
                        'rating_count': rating_count
                    }
                )

            return Response({'status': 'success'})
        finally:
            await prisma.disconnect()
>>>>>>> 521318b5f2f30b230af1e4fd3d826e69daa0432c
