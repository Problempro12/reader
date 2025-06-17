import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class GoogleBooksAPI:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1"
        self.api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        if not self.api_key:
            logger.warning("GOOGLE_BOOKS_API_KEY не найден в переменных окружения")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Выполняет запрос к Google Books API
        """
        try:
            if params is None:
                params = {}
            if self.api_key:
                params['key'] = self.api_key

            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Google Books API: {str(e)}")
            return None

    def search_books(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск книг по запросу
        """
        params = {
            'q': query,
            'maxResults': max_results
        }
        result = self._make_request('volumes', params)
        if result and 'items' in result:
            return [self._format_book(book) for book in result['items']]
        return []

    def get_book_details(self, book_id: str) -> Optional[Dict]:
        """
        Получение детальной информации о книге
        """
        result = self._make_request(f'volumes/{book_id}')
        if result:
            return self._format_book(result)
        return None

    def _format_book(self, book_data: Dict) -> Dict:
        """
        Форматирует данные книги из Google Books API в наш формат
        """
        volume_info = book_data.get('volumeInfo', {})
        return {
            'id': book_data.get('id'),
            'title': volume_info.get('title'),
            'authors': volume_info.get('authors', []),
            'description': volume_info.get('description'),
            'cover_url': volume_info.get('imageLinks', {}).get('thumbnail'),
            'publisher': volume_info.get('publisher'),
            'published_date': volume_info.get('publishedDate'),
            'isbn': self._get_isbn(volume_info.get('industryIdentifiers', [])),
            'page_count': volume_info.get('pageCount'),
            'language': volume_info.get('language'),
            'categories': volume_info.get('categories', []),
            'average_rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

    def _get_isbn(self, identifiers: List[Dict]) -> Optional[str]:
        """
        Извлекает ISBN из списка идентификаторов
        """
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                return identifier.get('identifier')
        return None

    def get_books_by_author(self, author: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск книг по автору
        """
        return self.search_books(f'inauthor:"{author}"', max_results)

    def get_books_by_title(self, title: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск книг по названию
        """
        return self.search_books(f'intitle:"{title}"', max_results)

    def get_books_by_isbn(self, isbn: str) -> List[Dict]:
        """
        Поиск книги по ISBN
        """
        return self.search_books(f'isbn:{isbn}')

    def get_books_by_category(self, category: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск книг по категории
        """
        return self.search_books(f'subject:"{category}"', max_results)

    def get_books_by_publisher(self, publisher: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск книг по издательству
        """
        return self.search_books(f'inpublisher:"{publisher}"', max_results) 