from typing import List, Optional
import httpx
import asyncio

class GoogleBooksAPI:
    def __init__(self):
        self.base_url = 'https://www.googleapis.com/books/v1'
        self.api_key = 'AIzaSyBNYj9MZIrdHkVYMKdQZZIjCjDiXk14Xh8'
        self.max_retries = 5
        self.retry_delay = 15

    async def search_books(self, query: str, max_results: int = 10) -> List[dict]:
        params = {
            'q': query,
            'key': self.api_key,
            'maxResults': max_results
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

    def map_google_genre_to_our_genre(self, categories: List[str]) -> Optional[int]:
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
        }

        for category in categories:
            for google_genre, our_genre_id in genre_mapping.items():
                if google_genre.lower() in category.lower():
                    return our_genre_id

        return None