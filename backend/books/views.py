from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from prisma import Prisma
from .serializers import BookSerializer, GenreSerializer, AgeCategorySerializer
from datetime import datetime
import asyncio
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from bs4 import BeautifulSoup
from asgiref.sync import async_to_sync
from django.db.models import Q
from .models import Book
from django.conf import settings
import json

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

class BookListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_queryset(self):
        async def get_books():
            prisma = Prisma()
            await prisma.connect()
            books = await prisma.book.find_many()
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

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_object(self):
        async def get_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.find_unique(where={'id': self.kwargs['pk']})
            await prisma.disconnect()
            return book
        return run_async(get_book())

    def perform_update(self, serializer):
        async def update_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.update(
                where={'id': self.kwargs['pk']},
                data=serializer.validated_data
            )
            await prisma.disconnect()
            return book
        return run_async(update_book())

    def perform_destroy(self, instance):
        async def delete_book():
            prisma = Prisma()
            await prisma.connect()
            await prisma.book.delete(where={'id': self.kwargs['pk']})
            await prisma.disconnect()
        run_async(delete_book())

class GenreListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenreSerializer

    def get_queryset(self):
        async def get_genres():
            prisma = Prisma()
            await prisma.connect()
            genres = await prisma.genre.find_many()
            await prisma.disconnect()
            return genres
        return run_async(get_genres())

class AgeCategoryListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgeCategorySerializer

    def get_queryset(self):
        async def get_categories():
            prisma = Prisma()
            await prisma.connect()
            categories = await prisma.agecategory.find_many()
            await prisma.disconnect()
            return categories
        return run_async(get_categories())

class VoteCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        async def create_vote():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            vote = await prisma.vote.create(
                data={
                    'userId': self.request.user.id,
                    'bookId': serializer.validated_data['bookId'],
                    'weekNumber': current_week,
                }
            )
            
            # После успешного голосования проверяем и выдаем достижения
            await check_and_award_achievements(self.request.user.id, prisma)

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

    async def post(self, request):
        """Получение информации о книге с LitRes по URL"""
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL не указан'}, status=400)

        try:
            print(f"Начинаем запрос к LitRes: {url}")
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

            # Ищем обложку в новой структуре
            cover = soup.select_one('img[itemprop="image"]')
            if not cover:
                print("Не найдена обложка")
                print("Доступные изображения:", [img.get('src') for img in soup.find_all('img')])
                return Response({'error': 'Не удалось найти обложку книги'}, status=400)
            cover = cover['src']
            print(f"Найдена обложка: {cover}")

            # Ищем описание в новой структуре
            description = soup.select_one('div.BookCard-module__30TmjW__truncate p')
            if not description:
                print("Не найдено описание")
                print("Доступные div с описанием:", [div.text[:100] for div in soup.find_all('div', class_='BookCard-module__30TmjW__truncate')])
                return Response({'error': 'Не удалось найти описание книги'}, status=400)
            description = description.text.strip()
            print(f"Найдено описание: {description[:100]}...")

            # Ищем жанры в новой структуре
            genres = []
            genre_elements = soup.select('div.BookGenresAndTags-module___lt2qq__genresList a.StyledLink-module__9cE5yW__link')
            for genre in genre_elements:
                genre_text = genre.text.strip()
                if genre_text and not genre_text.endswith(','):  # Убираем запятые
                    genres.append(genre_text)
            print(f"Найдены жанры: {genres}")

            # Находим или создаем жанры в базе данных
            genre_ids = []
            prisma = Prisma() # Создаем новый экземпляр Prisma для этой операции
            await prisma.connect() # Подключаемся к базе данных

            for genre_name in genres:
                print(f"Ищем жанр в базе данных: '{genre_name}'")
                # Ищем жанр в базе
                genre = await prisma.genre.find_first(
                    where={
                        'OR': [
                            {'name': genre_name},
                            {'subgenres': {'some': {'name': genre_name}}}
                        ]
                    }
                )

                if genre:
                    print(f"Жанр найдет в базе: '{genre.name}' (ID: {genre.id})")
                    genre_ids.append(genre.id)
                else:
                    # Если жанр не найден, создаем его
                    print(f"Жанр '{genre_name}' не найден. Создаем новый.")
                    try:
                        new_genre = await prisma.genre.create(
                            data={'name': genre_name}
                        )
                        print(f"Новый жанр создан: '{new_genre.name}' (ID: {new_genre.id})")
                        genre_ids.append(new_genre.id)
                    except Exception as create_error:
                        print(f"Ошибка при создании жанра '{genre_name}': {str(create_error)}")
                        # Можно добавить логику для пропуска этого жанра или возврата ошибки

            await prisma.disconnect() # Отключаемся от базы данных
            print(f"Все найденные/созданные ID жанров: {genre_ids}")

            # Ищем возрастной рейтинг в новой структуре
            age_rating_div = soup.select_one('div.CharacteristicsBlock-module__6QUqXW__characteristic:has(div.CharacteristicsBlock-module__6QUqXW__characteristic__title:contains("Возрастное ограничение"))')
            age_rating = None
            if age_rating_div:
                # Берем последний span, который содержит значение
                spans = age_rating_div.find_all('span')
                if len(spans) > 1:
                    age_rating = spans[-1].text.strip()
            print(f"Найден возрастной рейтинг: {age_rating}")

            # Ищем серию в новой структуре
            series = soup.select_one('div.BookDetailsHeader-module__CvBt5W__series a')
            series = series.text.strip() if series else None
            print(f"Найдена серия: {series}")

            # Ищем переводчика в новой структуре
            translator = soup.select_one('div.BookDetailsHeader-module__CvBt5W__persons:has(span:contains("переводчик")) a')
            translator = translator.text.strip() if translator else None
            print(f"Найден переводчик: {translator}")

            # Ищем техническую информацию в новой структуре
            volume_div = soup.select_one('div.CharacteristicsBlock-module__6QUqXW__characteristic:has(div.CharacteristicsBlock-module__6QUqXW__characteristic__title:contains("Объем"))')
            volume = None
            if volume_div:
                spans = volume_div.find_all('span')
                if len(spans) > 1:
                    volume = spans[-1].text.strip()
            print(f"Найден объем: {volume}")

            year_div = soup.select_one('div.CharacteristicsBlock-module__6QUqXW__characteristic:has(div.CharacteristicsBlock-module__6QUqXW__characteristic__title:contains("Дата написания"))')
            year = None
            if year_div:
                spans = year_div.find_all('span')
                if len(spans) > 1:
                    year = spans[-1].text.strip()
            print(f"Найдена дата написания: {year}")

            copyright_div = soup.select_one('div[data-testid="book__characteristicsCopyrightHolder"]')
            copyright_holder = None
            if copyright_div:
                spans = copyright_div.find_all('span')
                if len(spans) > 1:
                    copyright_holder = spans[-1].text.strip()
            print(f"Найден правообладатель: {copyright_holder}")

            # Ищем рейтинг в новой структуре
            rating = soup.select_one('div[itemprop="aggregateRating"]')
            rating_value = float(rating.select_one('meta[itemprop="ratingValue"]')['content']) if rating else None
            rating_count = int(rating.select_one('meta[itemprop="ratingCount"]')['content']) if rating else None
            print(f"Найден рейтинг: {rating_value} ({rating_count} оценок)")

            # Добавляем отладочную информацию
            print("\nОтладочная информация:")
            for div in soup.select('div.CharacteristicsBlock-module__6QUqXW__characteristic'):
                print(f"Характеристика: {div.text.strip()}")
                print("Все span элементы:", [span.text.strip() for span in div.find_all('span')])
                print("---")

            # Создаем книгу с жанрами
            book = await prisma.book.create(
                data={
                    'title': title,
                    'author': author,
                    'coverUrl': cover, # Исправил на coverUrl
                    'description': description,
                    # 'ageRating': age_rating, # Удалил, так как ageRating - связь
                    'series': series,
                    'translator': translator,
                    'litresRating': rating_value, # Исправил на litresRating
                    'litresRatingCount': rating_count, # Исправил на litresRatingCount
                    'volume': volume,
                    'year': year,
                    'copyrightHolder': copyright_holder,
                    'genres': {
                         'connect': [{'id': genre_id} for genre_id in genre_ids]
                     } if genre_ids else {}, # Добавил проверку genre_ids
                    'ageCategory': { # Добавляем связь с ageCategory
                        'connect': {'id': 1} # Временно используем ID 1, нужно будет найти правильный ID
                    }
                }
            )

            return Response({
                'id': book.id,
                'title': title,
                'author': author,
                'cover': cover,
                'description': description,
                'genres': genres,
                'age_rating': age_rating,
                'series': series,
                'translator': translator,
                'rating': {
                    'value': rating_value,
                    'count': rating_count
                },
                'technical': {
                    'volume': volume,
                    'year': year,
                    'copyright_holder': copyright_holder
                }
            })
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса к LitRes: {str(e)}")
            return Response({'error': f'Ошибка запроса к LitRes: {e}'}, status=500)
        except Exception as e:
            print(f"Ошибка при скрапинге или сохранении: {str(e)}")
            return Response({'error': str(e)}, status=500)

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

class BookViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prisma = Prisma()
        self.prisma.connect()

    def __del__(self):
        self.prisma.disconnect()

    def list(self, request):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('perPage', 12))
        search = request.query_params.get('search')
        genre = request.query_params.get('genre')
        age_category = request.query_params.get('ageCategory')
        rating = request.query_params.get('rating')
        sort_by = request.query_params.get('sortBy')

        # Базовый запрос
        query = {
            "skip": (page - 1) * per_page,
            "take": per_page,
            "include": {
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        }

        # Добавляем фильтры
        where = {}
        if search:
            where["OR"] = [
                {"title": {"contains": search}},
                {"author": {"name": {"contains": search}}}
            ]
        if genre:
            where["genre"] = {"name": genre}
        if age_category:
            where["ageCategory"] = {"name": age_category}
        if rating:
            where["rating"] = {"gte": float(rating)}

        if where:
            query["where"] = where

        # Добавляем сортировку
        if sort_by:
            if sort_by == "rating":
                query["order"] = {"rating": "desc"}
            elif sort_by == "newest":
                query["order"] = {"createdAt": "desc"}
            elif sort_by == "alphabet":
                query["order"] = {"title": "asc"}

        # Получаем книги
        books = self.prisma.book.find_many(**query)
        total = self.prisma.book.count(where=where if where else None)

        return Response({
            'books': books,
            'total': total,
            'page': page,
            'perPage': per_page
        })

    @action(detail=False, methods=['get'], url_path='top')
    def top(self, request):
        books = self.prisma.book.find_many(
            take=5,
            order={"rating": "desc"},
            include={
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        )
        return Response(books)

    @action(detail=False, methods=['get'], url_path='recommended')
    def recommended(self, request):
        # Здесь можно добавить более сложную логику рекомендаций
        books = self.prisma.book.find_many(
            take=5,
            order={"rating": "desc"},
            include={
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        )
        return Response(books)

    @action(detail=True, methods=['post'], url_path='rate')
    def rate(self, request, pk=None):
        rating = request.data.get('rating')
        
        if not rating or not isinstance(rating, (int, float)) or not 1 <= rating <= 5:
            return Response(
                {'error': 'Rating must be a number between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book = self.prisma.book.update(
            where={"id": int(pk)},
            data={
                "rating": rating,
                "rating_count": {"increment": 1}
            }
        )
        
        return Response(book)
