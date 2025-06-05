from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from prisma import Prisma
from .serializers import BookSerializer, GenreSerializer, AgeCategorySerializer
from datetime import datetime
import asyncio
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from bs4 import BeautifulSoup

def run_async(coro):
    return asyncio.run(coro)

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
            await prisma.disconnect()
            return vote
        return run_async(create_vote())

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def scrape_litres_view(request):
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
                'cover': cover,
                'description': description,
                'ageRating': age_rating,
                'series': series,
                'translator': translator,
                'rating': rating_value,
                'ratingCount': rating_count,
                'volume': volume,
                'year': year,
                'copyrightHolder': copyright_holder,
                'genres': {
                    'connect': [{'id': genre_id} for genre_id in genre_ids]
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
    except Exception as e:
        print(f"Ошибка при скрапинге: {str(e)}")
        return Response({'error': str(e)}, status=500)
