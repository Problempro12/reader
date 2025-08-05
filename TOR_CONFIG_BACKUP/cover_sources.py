"""Модуль для получения обложек книг из различных источников"""

import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote
import time

# Google Books API Key (используем тот же, что и в utils.py)
GOOGLE_BOOKS_API_KEY = "AIzaSyDuGTLUy05d8pBo6sWuXwdsX8NnUZxhWdg"

logger = logging.getLogger(__name__)

class CoverSourceManager:
    """Менеджер для получения обложек книг из различных источников"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_book_cover(self, title: str, author: str = None, flibusta_id: str = None) -> Optional[str]:
        """Получить URL обложки книги из различных источников"""
        
        # Если есть ID книги из Flibusta, сначала пробуем получить обложку оттуда
        if flibusta_id:
            cover_url = self._get_cover_from_flibusta_su(flibusta_id)
            if cover_url:
                return cover_url
        
        # Сначала пробуем Google Books API
        cover_url = self._get_cover_from_google_books(title, author)
        if cover_url:
            return cover_url
        
        # Если Google Books не дал результата, пробуем Open Library
        cover_url = self._get_cover_from_open_library(title, author)
        if cover_url:
            return cover_url
        
        # Если ничего не найдено, возвращаем заглушку
        return '/placeholder-book.svg'
    
    def _get_cover_from_google_books(self, title: str, author: str = None) -> Optional[str]:
        """Получить обложку из Google Books API"""
        if not GOOGLE_BOOKS_API_KEY or GOOGLE_BOOKS_API_KEY == "YOUR_GOOGLE_BOOKS_API_KEY":
            logger.warning("Google Books API Key не настроен")
            return None
        
        try:
            # Формируем поисковый запрос
            query_parts = [title]
            if author:
                query_parts.append(f"inauthor:{author}")
            
            query = ' '.join(query_parts)
            encoded_query = quote(query)
            
            url = f"https://www.googleapis.com/books/v1/volumes?q={encoded_query}&key={GOOGLE_BOOKS_API_KEY}&maxResults=5"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Ищем книгу с наилучшим совпадением
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                
                # Проверяем совпадение названия
                book_title = volume_info.get('title', '').lower()
                if self._is_title_match(title.lower(), book_title):
                    
                    # Получаем обложку
                    image_links = volume_info.get('imageLinks', {})
                    if image_links:
                        # Пытаемся получить изображение наивысшего качества
                        cover_url = (image_links.get('extraLarge') or 
                                   image_links.get('large') or 
                                   image_links.get('medium') or 
                                   image_links.get('small') or 
                                   image_links.get('thumbnail'))
                        
                        if cover_url:
                            # Улучшаем качество изображения
                            if 'zoom=1' in cover_url:
                                cover_url = cover_url.replace('zoom=1', 'zoom=0')
                            
                            # Конвертируем HTTP в HTTPS
                            if cover_url.startswith('http://'):
                                cover_url = cover_url.replace('http://', 'https://')
                            
                            logger.info(f"Найдена обложка в Google Books для '{title}': {cover_url}")
                            return cover_url
            
            logger.info(f"Обложка не найдена в Google Books для '{title}'")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении обложки из Google Books для '{title}': {e}")
            return None
    
    def _get_cover_from_flibusta_su(self, book_id: str) -> Optional[str]:
        """Получить обложку с Flibusta (flibusta.su и flibusta.is) по ID книги"""
        try:
            # Пробуем разные возможные URL для обложек на Flibusta
            # Основываясь на структуре из flibusta-api: /i/0/{book_id}/cover.jpg
            possible_urls = [
                # Сначала пробуем flibusta.su (зеркало)
                f"https://flibusta.su/i/0/{book_id}/cover.jpg",
                f"https://flibusta.su/i/{book_id}/cover.jpg", 
                f"https://flibusta.su/covers/{book_id}.jpg",
                # Затем пробуем основной сайт flibusta.is
                f"https://flibusta.is/i/0/{book_id}/cover.jpg",
                f"https://flibusta.is/i/{book_id}/cover.jpg",
                f"https://flibusta.is/covers/{book_id}.jpg",
                # Дополнительные варианты
                f"https://flibusta.su/i/book/{book_id}.jpg",
                f"https://flibusta.su/img/book/{book_id}.jpg",
                f"https://flibusta.su/static/covers/{book_id}.jpg"
            ]
            
            for cover_url in possible_urls:
                try:
                    response = self.session.head(cover_url, timeout=5)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        if content_type.startswith('image/'):
                            logger.info(f"Найдена обложка на Flibusta для ID {book_id}: {cover_url}")
                            return cover_url
                except Exception:
                    continue
            
            logger.info(f"Обложка не найдена на Flibusta для ID {book_id}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении обложки с Flibusta для ID {book_id}: {e}")
            return None
    
    def _get_cover_from_open_library(self, title: str, author: str = None) -> Optional[str]:
        """Получить обложку из Open Library API"""
        try:
            # Формируем поисковый запрос для Open Library
            query_parts = [title]
            if author:
                query_parts.append(author)
            
            query = ' '.join(query_parts)
            encoded_query = quote(query)
            
            url = f"https://openlibrary.org/search.json?q={encoded_query}&limit=5"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Ищем книгу с наилучшим совпадением
            for doc in data.get('docs', []):
                book_title = doc.get('title', '').lower()
                
                if self._is_title_match(title.lower(), book_title):
                    # Получаем ID обложки
                    cover_i = doc.get('cover_i')
                    if cover_i:
                        # Формируем URL обложки (размер L = большой)
                        cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
                        logger.info(f"Найдена обложка в Open Library для '{title}': {cover_url}")
                        return cover_url
            
            logger.info(f"Обложка не найдена в Open Library для '{title}'")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении обложки из Open Library для '{title}': {e}")
            return None
    
    def _is_title_match(self, search_title: str, book_title: str) -> bool:
        """Проверить, совпадают ли названия книг"""
        # Простая проверка на совпадение
        search_words = set(search_title.split())
        book_words = set(book_title.split())
        
        # Если больше половины слов совпадают, считаем это совпадением
        if len(search_words) == 0:
            return False
        
        common_words = search_words.intersection(book_words)
        match_ratio = len(common_words) / len(search_words)
        
        return match_ratio >= 0.5
    
    def update_book_cover(self, book_title: str, author_name: str = None, flibusta_id: str = None) -> Optional[str]:
        """Обновить обложку книги и вернуть URL"""
        return self.get_book_cover(book_title, author_name, flibusta_id)

# Глобальный экземпляр менеджера
cover_manager = CoverSourceManager()

def get_book_cover_url(title: str, author: str = None, flibusta_id: str = None) -> str:
    """Получить URL обложки книги (основная функция для использования)"""
    logger.info(f"Поиск обложки для: '{title}' автор: '{author}' flibusta_id: '{flibusta_id}'")
    result = cover_manager.get_book_cover(title, author, flibusta_id) or '/placeholder-book.svg'
    logger.info(f"Результат поиска обложки: {result}")
    return result

def update_existing_books_covers():
    """Обновить обложки для существующих книг в базе данных"""
    from .models import Book
    from django.db import models
    
    books_without_covers = Book.objects.filter(
        models.Q(cover_url__isnull=True) | 
        models.Q(cover_url='') | 
        models.Q(cover_url='/placeholder-book.svg')
    )
    
    updated_count = 0
    
    for book in books_without_covers:
        try:
            new_cover_url = get_book_cover_url(book.title, book.author.name)
            if new_cover_url:
                book.cover_url = new_cover_url
                book.save()
                updated_count += 1
                if new_cover_url == '/placeholder-book.svg':
                    logger.info(f"Установлена заглушка обложки для книги '{book.title}'")
                else:
                    logger.info(f"Обновлена обложка для книги '{book.title}': {new_cover_url}")
                
                # Небольшая задержка, чтобы не перегружать API
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении обложки для книги '{book.title}': {e}")
    
    logger.info(f"Обновлено обложек: {updated_count}")
    return updated_count