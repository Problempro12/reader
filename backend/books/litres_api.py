import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LitresAPI:
    def __init__(self):
        self.base_url = "https://api.litres.ru/foundation/api"
        self.api_key = os.getenv('LITRES_API_KEY')
        if not self.api_key:
            logger.warning("LITRES_API_KEY не найден в переменных окружения")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Выполняет запрос к API Литрес
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к API Литрес: {str(e)}")
            return None

    def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Поиск книг по запросу
        """
        params = {
            'q': query,
            'limit': limit,
            'type': 'book'
        }
        result = self._make_request('search', params)
        if result and 'items' in result:
            return result['items']
        return []

    def get_book_details(self, book_id: str) -> Optional[Dict]:
        """
        Получение детальной информации о книге
        """
        result = self._make_request(f'books/{book_id}')
        if result:
            return {
                'id': result.get('id'),
                'title': result.get('title'),
                'author': result.get('author', {}).get('name'),
                'description': result.get('description'),
                'cover_url': result.get('cover', {}).get('url'),
                'rating': result.get('rating', {}).get('value'),
                'rating_count': result.get('rating', {}).get('count'),
                'price': result.get('price', {}).get('value'),
                'currency': result.get('price', {}).get('currency'),
                'isbn': result.get('isbn'),
                'year': result.get('year'),
                'pages': result.get('pages'),
                'language': result.get('language'),
                'publisher': result.get('publisher', {}).get('name'),
                'genres': [genre.get('name') for genre in result.get('genres', [])],
                'age_restriction': result.get('age_restriction'),
                'available_formats': result.get('available_formats', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        return None

    def get_book_rating(self, book_id: str) -> Optional[Dict]:
        """
        Получение рейтинга книги
        """
        result = self._make_request(f'books/{book_id}/rating')
        if result:
            return {
                'rating': result.get('value'),
                'count': result.get('count'),
                'distribution': result.get('distribution', {})
            }
        return None

    def get_book_reviews(self, book_id: str, limit: int = 10) -> List[Dict]:
        """
        Получение отзывов о книге
        """
        params = {
            'limit': limit
        }
        result = self._make_request(f'books/{book_id}/reviews', params)
        if result and 'items' in result:
            return result['items']
        return []

    def get_author_books(self, author_id: str, limit: int = 10) -> List[Dict]:
        """
        Получение книг автора
        """
        params = {
            'limit': limit
        }
        result = self._make_request(f'authors/{author_id}/books', params)
        if result and 'items' in result:
            return result['items']
        return []

    def get_popular_books(self, limit: int = 10) -> List[Dict]:
        """
        Получение популярных книг
        """
        params = {
            'limit': limit,
            'sort': 'popularity'
        }
        result = self._make_request('books', params)
        if result and 'items' in result:
            return result['items']
        return []

    def get_new_books(self, limit: int = 10) -> List[Dict]:
        """
        Получение новых книг
        """
        params = {
            'limit': limit,
            'sort': 'date'
        }
        result = self._make_request('books', params)
        if result and 'items' in result:
            return result['items']
        return [] 