from typing import List, Optional, Dict, Any
import httpx
import asyncio
from datetime import datetime

class GoogleBooksAPI:
    def __init__(self):
        self.base_url = 'https://www.googleapis.com/books/v1'
        self.api_key = 'AIzaSyBNYj9MZIrdHkVYMKdQZZIjCjDiXk14Xh8'
        self.max_retries = 5
        self.retry_delay = 15

    async def search_books(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Поиск книг через Google Books API.
        """
        params = {
            'q': query,
            'key': self.api_key,
            'maxResults': max_results,
            'langRestrict': 'ru'  # Ограничиваем поиск русскими книгами
        }
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(f"{self.base_url}/volumes", params=params)
                    response.raise_for_status()
                    data = response.json()
                    print(f"\nПоиск по запросу '{query}':")
                    print(f"Найдено книг: {data.get('totalItems', 0)}")
                    if 'items' in data:
                        print(f"Пример первой книги: {data['items'][0]['volumeInfo'].get('title')}")
                    return data.get('items', [])
                except httpx.HTTPStatusError as e:
                    print(f"HTTP ошибка при поиске книг: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise
                except httpx.RequestError as e:
                    print(f"Ошибка запроса при поиске книг: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

    async def get_book_details(self, book_id: str) -> Optional[dict]:
        """
        Получение детальной информации о книге по ID.
        """
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(f"{self.base_url}/volumes/{book_id}", params={'key': self.api_key})
                    response.raise_for_status()
                    book_data = response.json()
                    print(f"\nПолучены детали книги {book_id}: {list(book_data.keys())}")
                    return book_data
                except httpx.HTTPStatusError as e:
                    print(f"HTTP ошибка при получении деталей книги {book_id}: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    return None
                except httpx.RequestError as e:
                    print(f"Ошибка запроса при получении деталей книги {book_id}: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    return None

    async def get_book_by_isbn(self, isbn: str) -> Optional[dict]:
        """
        Получение информации о книге по ISBN.
        """
        books = await self.search_books(f"isbn:{isbn}", max_results=1)
        if not books:
            return None
        return await self.get_book_details(books[0]['id'])

    def map_google_genre_to_our_genre(self, categories: List[str]) -> Optional[int]:
        """
        Маппинг жанров из Google Books в наши жанры.
        """
        if not categories:
            return None

        genre_mapping = {
            'Fiction': 1,
            'Fantasy': 1,
            'Science Fiction': None,  # Для автоматического создания жанра
            'Mystery & Detective': 2,
            'Thriller': 2,
            'Romance': 2,
            'Horror': 1,
            'Poetry': 2,
            'Drama': 2,
            'Classic': 1,
            'Adventure': 1,
            'Historical Fiction': 1,
            'Literary Fiction': 1,
            'Contemporary': 2,
            'Young Adult': 2,
            'Children': 2,
            'Biography': 2,
            'History': 2,
            'Science': 2,
            'Technology': 2,
            'Philosophy': 2,
            'Psychology': 2,
            'Self-Help': 2,
            'Business': 2,
            'Economics': 2,
            'Politics': 2,
            'Religion': 2,
            'Spirituality': 2,
            'Art': 2,
            'Music': 2,
            'Sports': 2,
            'Travel': 2,
            'Cooking': 2,
            'Health': 2,
            'Fitness': 2,
            'Education': 2,
            'Language': 2,
            'Reference': 2,
            'Comics': 2,
            'Graphic Novels': 2,
            'Manga': 2,
            'Humor': 2,
            'Satire': 2,
            'Parody': 2,
            'Fable': 2,
            'Fairy Tale': 2,
            'Folklore': 2,
            'Mythology': 2,
            'Legend': 2,
            'Epic': 2,
            'Saga': 2,
            'Short Stories': 2,
            'Anthology': 2,
            'Collection': 2,
            'Essays': 2,
            'Letters': 2,
            'Diary': 2,
            'Memoir': 2,
            'Autobiography': 2,
            'True Crime': 2,
            'Journalism': 2,
            'Reportage': 2,
            'Documentary': 2,
            'Textbook': 2,
            'Guide': 2,
            'Manual': 2,
            'Handbook': 2,
            'Dictionary': 2,
            'Encyclopedia': 2,
            'Almanac': 2,
            'Yearbook': 2,
            'Calendar': 2,
            'Atlas': 2,
            'Map': 2,
            'Chart': 2,
            'Diagram': 2,
            'Illustration': 2,
            'Photography': 2,
            'Art Book': 2,
            'Catalog': 2,
            'Exhibition': 2,
            'Collection': 2,
            'Series': 2,
            'Trilogy': 2,
            'Tetralogy': 2,
            'Pentalogy': 2,
            'Hexalogy': 2,
            'Heptalogy': 2,
            'Octology': 2,
            'Nonology': 2,
            'Decalogy': 2,
        }

        for category in categories:
            for google_genre, our_genre_id in genre_mapping.items():
                if google_genre.lower() in category.lower():
                    return our_genre_id

        return None