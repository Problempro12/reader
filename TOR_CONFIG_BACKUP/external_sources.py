"""Модуль для работы с внешними источниками книг (только Флибуста)"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import time
import random
import chardet
import zipfile
import io
from urllib.parse import urljoin, urlparse
from .external_config import (
    FLIBUSTA_CONFIG,
    EXTERNAL_SOURCES_CONFIG,
    SECURITY_CONFIG,
    TOR_PROXY_CONFIG
)
from .cover_sources import get_book_cover_url
from requests import Session
import json
import xml.etree.ElementTree as ET
from datetime import datetime


class FlibustaTorClient:
    """Клиент для работы с Флибустой через Tor"""
    
    def __init__(self, use_tor: bool = True):
        self.session = Session()
        self.use_tor = use_tor
        self.logger = logging.getLogger(__name__)
        
        # Используем только onion-адрес через Tor SOCKS прокси
        if use_tor:
            # Настройка SOCKS прокси для onion-адресов
            if TOR_PROXY_CONFIG:
                self.session.proxies.update(TOR_PROXY_CONFIG)
                self.logger.info(f"Настроен SOCKS прокси: {TOR_PROXY_CONFIG}")
            
            self.base_url = FLIBUSTA_CONFIG['onion_url']
            self.logger.info(f"Подключение к onion-адресу через Tor SOCKS прокси: {self.base_url}")
        else:
            raise ValueError("Подключение к Flibusta возможно только через Tor!")
        
        self.opds_url = f"{self.base_url}/opds"
        
        # Настройка retry стратегии
        retry_strategy = Retry(
            total=FLIBUSTA_CONFIG['max_retries'],
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Настройка заголовков
        self.session.headers.update({
            'User-Agent': EXTERNAL_SOURCES_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Настройка таймаутов
        self.timeout = FLIBUSTA_CONFIG['timeout']
    
    def search_books(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск книг на Флибусте через Tor"""
        books = []
        
        try:
            # Поиск через OPDS только через Tor
            books = self._search_via_opds(query, limit)
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска на Флибусте через Tor: {e}")
        
        return books
    
    def browse_categories(self) -> List[Dict[str, Any]]:
        """Получить список доступных категорий/жанров"""
        try:
            # Используем прямую ссылку /g для получения всех жанров
            genres_url = f"{self.base_url}/g"
            self.logger.info(f"Запрос жанров: {genres_url}")
            
            response = self.session.get(genres_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            categories = []
            
            # Ищем все ссылки на жанры на странице /g
            import re
            genre_links = soup.find_all('a', href=re.compile(r'/g/\d+'))
            
            for link in genre_links:
                genre_text = link.get_text(strip=True)
                if genre_text and len(genre_text) > 1:  # Исключаем пустые или слишком короткие названия
                    # Извлекаем ID жанра из href
                    href = link.get('href', '')
                    genre_id_match = re.search(r'/g/(\d+)', href)
                    if genre_id_match:
                        genre_id = genre_id_match.group(1)
                        categories.append({
                            'id': genre_id,
                            'name': genre_text,
                            'url': f"{self.base_url}{href}"
                        })
            
            # Удаляем дубликаты по ID
            seen_ids = set()
            unique_categories = []
            for cat in categories:
                if cat['id'] not in seen_ids:
                    seen_ids.add(cat['id'])
                    unique_categories.append(cat)
            
            self.logger.info(f"Найдено {len(unique_categories)} уникальных категорий")
            return unique_categories
            
        except Exception as e:
            self.logger.error(f"Ошибка получения категорий: {e}")
            return []
    
    def browse_books_by_category(self, category_url: str, sort_by_popularity: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить книги из категории с сортировкой по популярности"""
        try:
            response = self.session.get(category_url, timeout=self.timeout)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            books = []
            
            # Namespace для OPDS
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opds': 'http://opds-spec.org/2010/catalog'
            }
            
            entries = root.findall('.//atom:entry', ns)
            
            # Если это каталог подкategorий, ищем ссылку на "популярные" или "топ"
            if sort_by_popularity:
                for entry in entries:
                    title_elem = entry.find('atom:title', ns)
                    if title_elem is not None:
                        title = title_elem.text.strip().lower()
                        
                        if any(keyword in title for keyword in ['популярн', 'топ', 'popular', 'top', 'best']):
                            for link in entry.findall('atom:link', ns):
                                href = link.get('href')
                                link_type = link.get('type')
                                
                                if href and link_type == 'application/atom+xml;profile=opds-catalog':
                                    popular_url = href if href.startswith('http') else f"{self.base_url}{href}"
                                    return self._get_books_from_catalog(popular_url, limit)
            
            # Если не нашли популярные, получаем все книги из категории
            return self._get_books_from_catalog(category_url, limit)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения книг из категории: {e}")
            return []
    
    def _get_books_from_catalog(self, catalog_url: str, limit: int) -> List[Dict[str, Any]]:
        """Получить книги из каталога"""
        try:
            response = self.session.get(catalog_url, timeout=self.timeout)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            books = []
            
            # Namespace для OPDS
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opds': 'http://opds-spec.org/2010/catalog'
            }
            
            entries = root.findall('.//atom:entry', ns)
            
            for entry in entries[:limit]:
                book_data = self._parse_book_entry(entry, ns)
                if book_data:
                    books.append(book_data)
            
            return books
            
        except Exception as e:
            self.logger.error(f"Ошибка получения книг из каталога {catalog_url}: {e}")
            return []
    
    def _get_categories_from_catalog(self, catalog_url: str, limit: int) -> List[Dict[str, Any]]:
        """Получить категории/жанры из каталога (без фильтрации по ссылкам скачивания)"""
        try:
            response = self.session.get(catalog_url, timeout=self.timeout)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            categories = []
            
            # Namespace для OPDS
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'opds': 'http://opds-spec.org/2010/catalog'
            }
            
            entries = root.findall('.//atom:entry', ns)
            
            for entry in entries[:limit]:
                # Парсим как категорию (без фильтрации по ссылкам скачивания)
                category_data = self._parse_category_entry(entry, ns)
                if category_data:
                    categories.append(category_data)
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Ошибка получения категорий из каталога {catalog_url}: {e}")
            return []
    
    def _parse_category_entry(self, entry, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Парсинг элемента каталога как категории/жанра"""
        try:
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text if title_elem is not None else 'Без названия'
            
            # Ищем ссылку на категорию
            category_url = None
            links = entry.findall('atom:link', ns)
            
            for link in links:
                rel = link.get('rel', '')
                href = link.get('href', '')
                
                # Ищем ссылку на подкаталог или навигацию
                if rel in ['subsection', 'alternate'] or 'type' in link.attrib:
                    if href:
                        category_url = urljoin(self.base_url, href)
                        break
            
            # Если не нашли специальную ссылку, берем первую доступную
            if not category_url and links:
                href = links[0].get('href', '')
                if href:
                    category_url = urljoin(self.base_url, href)
            
            if not category_url:
                return None
            
            return {
                'title': title,
                'url': category_url,
                'download_url': category_url  # Для совместимости
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга элемента категории: {e}")
            return None
    
    def _search_via_opds(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Поиск через OPDS каталог"""
        search_url = f"{self.opds_url}/search?searchTerm={query}"
        response = self.session.get(search_url, timeout=self.timeout)
        response.raise_for_status()
        
        # Парсим OPDS XML
        root = ET.fromstring(response.content)
        books = []
        
        # Namespace для OPDS
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opds': 'http://opds-spec.org/2010/catalog'
        }
        
        entries = root.findall('.//atom:entry', ns)
        
        # Ищем поисковые ссылки в первоначальном ответе
        search_links = []
        for entry in entries:
            title_elem = entry.find('atom:title', ns)
            if title_elem is not None and title_elem.text:
                title_text = title_elem.text.strip()
                
                # Ищем только ссылки на поиск книг (не авторов)
                if any(search_term in title_text for search_term in ['Поиск книг', 'Search books']):
                    for link in entry.findall('atom:link', ns):
                        href = link.get('href')
                        link_type = link.get('type')
                        if href and link_type == 'application/atom+xml;profile=opds-catalog':
                            search_links.append((title_text, href))
                            break
        
        # Если найдены поисковые ссылки, переходим по ним
        if search_links:
            for search_type, search_href in search_links:
                if len(books) >= limit:
                    break
                    
                try:
                    # Формируем полный URL для поиска с запросом
                    if search_href.startswith('/'):
                        full_url = f"{self.base_url}{search_href}"
                    else:
                        full_url = urljoin(self.base_url, search_href)
                    
                    # Добавляем параметр поиска если его нет
                    if '?' not in full_url:
                        full_url += f"?searchTerm={query}"
                    elif 'searchTerm=' not in full_url:
                        full_url += f"&searchTerm={query}"
                    
                    self.logger.info(f"Переходим по ссылке {search_type}: {full_url}")
                    
                    # Получаем результаты поиска
                    search_response = self.session.get(full_url, timeout=self.timeout)
                    search_response.raise_for_status()
                    
                    # Парсим результаты
                    search_root = ET.fromstring(search_response.content)
                    search_entries = search_root.findall('.//atom:entry', ns)
                    
                    for entry in search_entries:
                        if len(books) >= limit:
                            break
                            
                        book_data = self._parse_book_entry(entry, ns)
                        if book_data:
                            books.append(book_data)
                            
                except Exception as e:
                    self.logger.warning(f"Ошибка при переходе по ссылке {search_type}: {e}")
                    continue
        else:
            # Если это уже результаты поиска, парсим их напрямую
            for entry in entries[:limit]:
                book_data = self._parse_book_entry(entry, ns)
                if book_data:
                    books.append(book_data)
        
        return books
    
    def _parse_book_entry(self, entry, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Парсинг одной записи книги из OPDS"""
        try:
            title = entry.find('atom:title', ns)
            author = entry.find('atom:author/atom:name', ns)
            summary = entry.find('atom:summary', ns)
            updated = entry.find('atom:updated', ns)
            
            # Пропускаем служебные записи
            if title is not None:
                title_text = title.text.strip()
                if any(skip_word in title_text for skip_word in ['Поиск', 'Search', 'Каталог', 'Catalog']):
                    return None
            
            # Проверяем, есть ли ссылки для скачивания (acquisition) - это отличает книги от категорий
            has_download_links = False
            for link in entry.findall('atom:link', ns):
                rel = link.get('rel')
                if rel in ['http://opds-spec.org/acquisition', 'http://opds-spec.org/acquisition/open-access']:
                    has_download_links = True
                    break
            
            # Если нет ссылок для скачивания, это скорее всего категория, а не книга
            if not has_download_links:
                return None
            
            # Извлекаем категории/жанры
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                label = category.get('label')
                if term:
                    categories.append(term)
                elif label:
                    categories.append(label)
            
            # Объединяем категории в строку жанра
            genre = ', '.join(categories) if categories else ''
            
            # Ищем ссылки на скачивание и обложки
            download_links = []
            cover_url = None
            
            for link in entry.findall('atom:link', ns):
                rel = link.get('rel')
                href = link.get('href')
                link_type = link.get('type', '')
                
                # Ищем ссылки для скачивания (acquisition)
                if rel in ['http://opds-spec.org/acquisition', 'http://opds-spec.org/acquisition/open-access']:
                    format_name = self._extract_format_from_type(link_type)
                    
                    if href and format_name:
                        # Формируем полный URL
                        if href.startswith('/'):
                            full_url = f"{self.base_url}{href}"
                        else:
                            full_url = href
                            
                        download_links.append({
                            'format': format_name,
                            'url': full_url,
                            'type': link_type
                        })
                
                # Ищем ссылки на обложки
                elif rel in ['http://opds-spec.org/image', 'http://opds-spec.org/image/thumbnail']:
                    if href and link_type.startswith('image/'):
                        # Формируем полный URL для обложки
                        if href.startswith('/'):
                            cover_url = f"{self.base_url}{href}"
                        else:
                            cover_url = href
            
            # Извлекаем ID книги из ссылок
            book_id = self._extract_book_id_from_links(download_links)
            
            # Если обложка не найдена в OPDS, пытаемся получить из внешних источников
            if not cover_url:
                title_text = title.text.strip() if title is not None else 'Без названия'
                author_text = author.text.strip() if author is not None else None
                
                # Получаем обложку, передавая ID книги для flibusta.su
                cover_url = get_book_cover_url(title_text, author_text, book_id)
                self.logger.info(f"Получена обложка для '{title_text}' (ID: {book_id}): {cover_url}")
            
            return {
                'title': title.text.strip() if title is not None else 'Без названия',
                'author': author.text.strip() if author is not None else 'Неизвестный автор',
                'description': summary.text.strip() if summary is not None else '',
                'updated': updated.text if updated is not None else '',
                'download_links': download_links,
                'source': 'flibusta',
                'source_id': book_id,
                'genre': genre,
                'cover_url': cover_url
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга записи книги: {e}")
            return None
    

    
    def _extract_format_from_type(self, mime_type: str) -> str:
        """Извлечение формата файла из MIME типа"""
        format_mapping = {
            'application/fb2+xml': 'fb2',
            'application/epub+zip': 'epub',
            'application/x-mobipocket-ebook': 'mobi',
            'text/plain': 'txt',
            'application/pdf': 'pdf'
        }
        return format_mapping.get(mime_type, mime_type.split('/')[-1])
    
    def _extract_book_id_from_links(self, download_links: List[Dict]) -> Optional[str]:
        """Извлечение ID книги из ссылок на скачивание"""
        for link in download_links:
            url = link.get('url', '')
            # Пример: /b/12345/download -> 12345
            if '/b/' in url:
                parts = url.split('/b/')
                if len(parts) > 1:
                    book_id = parts[1].split('/')[0]
                    if book_id.isdigit():
                        return book_id
        return None
    
    def _parse_opds_entry(self, entry, namespaces: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Парсинг одной записи из OPDS"""
        try:
            title_elem = entry.find('atom:title', namespaces)
            title = title_elem.text if title_elem is not None else "Неизвестное название"
            
            author_elem = entry.find('atom:author/atom:name', namespaces)
            author = author_elem.text if author_elem is not None else "Неизвестный автор"
            
            summary_elem = entry.find('atom:summary', namespaces)
            description = summary_elem.text if summary_elem is not None else ""
            
            # Поиск ссылок на скачивание
            download_links = {}
            links = entry.findall('atom:link', namespaces)
            
            for link in links:
                rel = link.get('rel')
                href = link.get('href')
                type_attr = link.get('type')
                
                if rel == 'http://opds-spec.org/acquisition':
                    if 'fb2' in type_attr:
                        download_links['fb2'] = urljoin(self.base_url, href)
                    elif 'epub' in type_attr:
                        download_links['epub'] = urljoin(self.base_url, href)
                    elif 'txt' in type_attr:
                        download_links['txt'] = urljoin(self.base_url, href)
            
            # Извлекаем ID книги из ссылок для получения обложки
            book_id = self._extract_book_id_from_links([{'url': link['url']} for link in download_links.values()])
            
            # Получаем обложку из внешних источников, передавая ID книги
            cover_url = get_book_cover_url(title, author, book_id)
            
            return {
                'title': title,
                'author': author,
                'description': description,
                'download_links': download_links,
                'source': 'flibusta',
                'source_id': book_id,
                'cover_url': cover_url
            }
            
        except Exception as e:
            print(f"Ошибка парсинга записи OPDS: {e}")
            return None
    
    def download_book(self, book_data: Dict[str, Any], format_preference: str = 'fb2') -> Optional[str]:
        """Скачивание книги с Флибусты"""
        try:
            download_links = book_data.get('download_links', [])
            
            if not download_links:
                # Если нет прямых ссылок, пробуем получить их через ID книги
                source_id = book_data.get('source_id')
                if source_id:
                    download_links = self._get_download_links_by_id(source_id)
            
            # Ищем предпочитаемый формат (включая архивы)
            preferred_link = None
            for link in download_links:
                link_format = link.get('format', '')
                # Проверяем точное совпадение или формат+zip
                if (link_format == format_preference or 
                    link_format == f"{format_preference}+zip" or
                    link_format.startswith(f"{format_preference}+")):
                    preferred_link = link
                    break
            
            # Если предпочитаемый формат не найден, ищем только FB2 или EPUB (включая архивы)
            if not preferred_link and download_links:
                # Строгий приоритет: fb2 (включая fb2+zip) > epub
                format_priority = ['fb2', 'epub']
                for fmt in format_priority:
                    for link in download_links:
                        link_format = link.get('format', '')
                        if (link_format == fmt or 
                            link_format == f"{fmt}+zip" or
                            link_format.startswith(f"{fmt}+")):
                            preferred_link = link
                            break
                    if preferred_link:
                        break
                
                # Если нет FB2 или EPUB, пропускаем книгу
                if not preferred_link:
                    self.logger.info(f"Пропускаем книгу '{book_data.get('title')}' - нет FB2 или EPUB форматов")
                    return None
            
            if not preferred_link:
                self.logger.error(f"Нет доступных ссылок для скачивания книги: {book_data.get('title')}")
                return None
            
            # Скачиваем файл
            download_url = preferred_link['url']
            if not download_url.startswith('http'):
                download_url = urljoin(self.base_url, download_url)
            
            self.logger.info(f"Скачивание книги: {book_data.get('title')} в формате {preferred_link.get('format')}")
            
            response = self.session.get(download_url, timeout=self.timeout * 2, stream=True)
            response.raise_for_status()
            
            # Проверяем размер файла
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > EXTERNAL_SOURCES_CONFIG['max_file_size']:
                self.logger.error(f"Файл слишком большой: {content_length} байт")
                return None
            
            # Получаем содержимое
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > EXTERNAL_SOURCES_CONFIG['max_file_size']:
                    self.logger.error("Превышен максимальный размер файла")
                    return None
            
            # Определяем кодировку и декодируем
            return self._decode_content(content, preferred_link.get('format', 'fb2'))
            
        except Exception as e:
            self.logger.error(f"Ошибка скачивания с Флибусты: {e}")
            return None
    
    def _get_download_links_by_id(self, book_id: str) -> List[Dict[str, Any]]:
        """Получение ссылок на скачивание по ID книги"""
        try:
            book_url = f"{self.base_url}/b/{book_id}"
            response = self.session.get(book_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            download_links = []
            
            # Ищем ссылки на скачивание в HTML
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if '/b/' in href and '/download' in href:
                    # Определяем формат по тексту ссылки или URL
                    link_text = link.text.lower()
                    format_name = 'fb2'  # по умолчанию
                    
                    for fmt in FLIBUSTA_CONFIG['supported_formats']:
                        if fmt in link_text or fmt in href:
                            format_name = fmt
                            break
                    
                    download_links.append({
                        'format': format_name,
                        'url': urljoin(self.base_url, href)
                    })
            
            return download_links
            
        except Exception as e:
            self.logger.error(f"Ошибка получения ссылок для книги {book_id}: {e}")
            return []
    
    def _decode_content(self, content: bytes, file_format: str) -> str:
        """Декодирование содержимого файла"""
        try:
            # Проверяем, является ли файл ZIP архивом
            if self._is_zip_archive(content):
                return self._extract_from_zip(content, file_format)
            
            # Для текстовых форматов пытаемся определить кодировку
            if file_format in ['fb2', 'txt']:
                if EXTERNAL_SOURCES_CONFIG['encoding_detection']:
                    detected = chardet.detect(content)
                    encoding = detected.get('encoding', 'utf-8')
                    confidence = detected.get('confidence', 0)
                    
                    if confidence > 0.7:
                        try:
                            return content.decode(encoding)
                        except UnicodeDecodeError:
                            pass
                
                # Пробуем стандартные кодировки
                for encoding in ['utf-8', 'windows-1251', 'cp1251', 'koi8-r']:
                    try:
                        return content.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                
                # В крайнем случае игнорируем ошибки
                return content.decode('utf-8', errors='ignore')
            
            elif file_format == 'epub':
                # Обработка EPUB файлов
                return self._parse_epub(content)
            
            else:
                # Для бинарных форматов возвращаем как есть (base64 или hex)
                import base64
                return base64.b64encode(content).decode('ascii')
                
        except Exception as e:
            self.logger.error(f"Ошибка декодирования содержимого: {e}")
            return content.decode('utf-8', errors='ignore')
    
    def _is_zip_archive(self, content: bytes) -> bool:
        """Проверка, является ли файл ZIP архивом"""
        try:
            return zipfile.is_zipfile(io.BytesIO(content))
        except Exception:
            return False
    
    def _extract_from_zip(self, content: bytes, expected_format: str) -> str:
        """Извлечение содержимого из ZIP архива"""
        try:
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_file:
                # Получаем список файлов в архиве
                file_list = zip_file.namelist()
                
                # Ищем файл нужного формата
                target_file = None
                format_extensions = {
                    'fb2': ['.fb2'],
                    'epub': ['.epub'],
                    'txt': ['.txt'],
                    'pdf': ['.pdf'],
                    'mobi': ['.mobi']
                }
                
                # Сначала ищем файл с нужным расширением
                if expected_format in format_extensions:
                    for ext in format_extensions[expected_format]:
                        for filename in file_list:
                            if filename.lower().endswith(ext):
                                target_file = filename
                                break
                        if target_file:
                            break
                
                # Если не найден, берем первый подходящий файл
                if not target_file:
                    for filename in file_list:
                        if not filename.endswith('/'):
                            for ext_list in format_extensions.values():
                                if any(filename.lower().endswith(ext) for ext in ext_list):
                                    target_file = filename
                                    break
                            if target_file:
                                break
                
                # Если все еще не найден, берем первый файл
                if not target_file and file_list:
                    target_file = file_list[0]
                
                if target_file:
                    # Извлекаем файл
                    extracted_content = zip_file.read(target_file)
                    
                    # Определяем формат по расширению файла
                    file_format = expected_format
                    for fmt, extensions in format_extensions.items():
                        if any(target_file.lower().endswith(ext) for ext in extensions):
                            file_format = fmt
                            break
                    
                    self.logger.info(f"Извлечен файл {target_file} из архива, формат: {file_format}")
                    
                    # Рекурсивно обрабатываем извлеченный файл
                    return self._decode_content(extracted_content, file_format)
                else:
                    self.logger.error("В архиве не найдено подходящих файлов")
                    return "Ошибка: в архиве не найдено подходящих файлов"
                    
        except Exception as e:
            self.logger.error(f"Ошибка извлечения из ZIP архива: {e}")
            return f"Ошибка извлечения из архива: {e}"
    
    def _parse_epub(self, content: bytes) -> str:
        """Парсинг EPUB файла для извлечения текста"""
        try:
            with zipfile.ZipFile(io.BytesIO(content), 'r') as epub_zip:
                # Ищем файлы с текстом (обычно в формате XHTML)
                text_parts = []
                
                for filename in epub_zip.namelist():
                    if filename.endswith(('.xhtml', '.html', '.htm')):
                        try:
                            file_content = epub_zip.read(filename)
                            # Парсим HTML/XHTML содержимое
                            soup = BeautifulSoup(file_content, 'html.parser')
                            
                            # Удаляем скрипты и стили
                            for script in soup(["script", "style"]):
                                script.decompose()
                            
                            # Извлекаем текст
                            text = soup.get_text()
                            
                            # Очищаем текст
                            lines = (line.strip() for line in text.splitlines())
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            text = '\n'.join(chunk for chunk in chunks if chunk)
                            
                            if text.strip():
                                text_parts.append(text)
                                
                        except Exception as e:
                            self.logger.warning(f"Ошибка обработки файла {filename} в EPUB: {e}")
                            continue
                
                if text_parts:
                    return '\n\n'.join(text_parts)
                else:
                    return "Ошибка: не удалось извлечь текст из EPUB файла"
                    
        except Exception as e:
            self.logger.error(f"Ошибка парсинга EPUB: {e}")
            return f"Ошибка парсинга EPUB: {e}"


# LibGenClient удален - используем только Flibusta


class ExternalBookSources:
    """Класс для работы с внешними источниками книг (только Flibusta)"""
    
    def __init__(self, use_tor_for_flibusta: bool = True):
        self.flibusta = FlibustaTorClient(use_tor=use_tor_for_flibusta)
    
    def search_flibusta(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск во Flibusta"""
        try:
            return self.flibusta.search_books(query, limit)
        except Exception as e:
            print(f"Ошибка поиска в Флибусте: {e}")
            return []
    
    def get_book_content(self, book_id: str, title: str, author: str, format_type: str = 'fb2') -> Optional[str]:
        """Получение содержимого книги из внешнего источника"""
        try:
            # Сначала ищем книгу
            search_query = f"{title} {author}"
            books = self.search_flibusta(search_query, limit=5)
            
            if not books:
                return None
            
            # Берем первую найденную книгу
            book_data = books[0]
            content = self.flibusta.download_book(book_data, format_type)
            if content:
                # Конвертация из FB2/EPUB в текст
                return self._convert_to_text(content, format_type)
            
            return None
            
        except Exception as e:
            print(f"Ошибка получения содержимого книги: {e}")
            return None
    
    def search_books_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск книг по категории во Флибусте"""
        try:
            # Получаем список категорий
            categories = self.flibusta.browse_categories()
            
            # Ищем нужную категорию
            category_url = None
            for cat in categories:
                if category.lower() in cat.get('name', '').lower():
                    category_url = cat.get('url')
                    break
            
            if not category_url:
                # Если категория не найдена, делаем обычный поиск
                return self.search_flibusta(category, limit)
            
            # Получаем книги из категории
            return self.flibusta.browse_books_by_category(category_url, sort_by_popularity=True, limit=limit)
            
        except Exception as e:
            print(f"Ошибка поиска по категории: {e}")
            return []
    
    def get_book_cover_url(self, book_id: str, title: str, author: str) -> Optional[str]:
        """Получение URL обложки книги"""
        try:
            return get_book_cover_url(title, author)
        except Exception as e:
            print(f"Ошибка получения обложки: {e}")
            return None
    
    def _convert_to_text(self, content: str, format_type: str) -> str:
        """Конвертация содержимого книги в текст"""
        try:
            if format_type == 'txt':
                return content
            elif format_type == 'fb2':
                # Парсинг FB2 XML
                return self._parse_fb2(content.encode('utf-8'))
            elif format_type == 'epub':
                # Для EPUB файлов контент уже должен быть обработан в _decode_content
                # Если это строка base64, декодируем и парсим
                try:
                    import base64
                    epub_bytes = base64.b64decode(content)
                    return self._parse_epub(epub_bytes)
                except Exception:
                    # Если не base64, возвращаем как есть
                    return content
            else:
                return content
        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return ""
    
    def _parse_fb2(self, fb2_content: bytes) -> str:
        """Парсинг FB2 файла для извлечения текста"""
        try:
            root = ET.fromstring(fb2_content)
            
            # FB2 namespace
            ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
            
            # Извлечение текста из секций
            text_parts = []
            
            # Поиск всех параграфов
            paragraphs = root.findall('.//fb:p', ns)
            for p in paragraphs:
                if p.text:
                    text_parts.append(p.text.strip())
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            print(f"Ошибка парсинга FB2: {e}")
            return ""


# Функции для интеграции с Django
def search_external_books(query: str, sources: List[str] = None, use_tor: bool = True, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """Поиск книг во внешних источниках (только Flibusta)
    
    Args:
        query: Поисковый запрос
        sources: Список источников для поиска
        use_tor: Если True - подключение к onion-адресу через VPN, если False - прямое подключение к clearnet зеркалам
        limit: Максимальное количество результатов
    """
    if sources is None:
        sources = ['flibusta']
    
    # use_tor=True: подключение к onion-адресу через VPN
    # use_tor=False: прямое подключение к clearnet зеркалам
    external_sources = ExternalBookSources(use_tor_for_flibusta=use_tor)
    
    results = {'flibusta': []}
    
    # Поиск только в Flibusta
    if 'flibusta' in sources:
        flibusta_results = external_sources.search_flibusta(query, limit)
        results['flibusta'] = flibusta_results
    
    return results


def import_book_from_external_source(book_data: Dict[str, Any], source: str, download_format: str = 'fb2', use_tor: bool = True) -> Optional[str]:
    """Импорт книги из внешнего источника (только Флибуста)
    
    Args:
        book_data: Данные книги
        source: Источник книги (только flibusta)
        download_format: Формат для скачивания (fb2, epub)
        use_tor: Использовать Tor для onion-адресов (по умолчанию True)
    """
    if source != 'flibusta':
        raise ValueError("Поддерживается только источник 'flibusta'")
    
    sources = ExternalBookSources(use_tor_for_flibusta=use_tor)
    return sources.get_book_content(book_data.get('id', ''), book_data.get('title', ''), book_data.get('author', ''), download_format)