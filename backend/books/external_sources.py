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
import html
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
            response = self.session.get(category_url, timeout=self.timeout)
            response.raise_for_status()
            self.logger.debug(f"Получен ответ от {category_url}, статус: {response.status_code}, размер: {len(response.content)} байт")

            # Проверяем кодировку, если не указана в заголовках
            encoding = response.encoding
            if not encoding or encoding == 'ISO-8859-1':
                encoding = chardet.detect(response.content)['encoding']
                self.logger.debug(f"Определена кодировка: {encoding}")

            # Декодируем контент с определенной кодировкой
            content = response.content.decode(encoding or 'utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            self.logger.debug(f"HTML успешно распарсен BeautifulSoup.")

            books = []
            # Логируем, что мы ищем книги
            self.logger.debug("Ищем книги в HTML...")

            # Находим все элементы 'div' с классом 'book'
            book_elements = soup.find_all('div', class_='book')
            self.logger.debug(f"Найдено {len(book_elements)} элементов 'div' с классом 'book'.")

            for i, book_elem in enumerate(book_elements):
                if len(books) >= limit:
                    self.logger.debug(f"Достигнут лимит книг ({limit}), прекращаем парсинг.")
                    break

                self.logger.debug(f"Обрабатываем элемент книги {i+1}/{len(book_elements)}...")
                book_data = self._parse_book_entry_bs(book_elem)
                if book_data:
                    books.append(book_data)
                    self.logger.debug(f"Книга добавлена: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                else:
                    self.logger.debug(f"Не удалось обработать элемент книги {i+1}.")

            self.logger.info(f"Завершено. Найдено {len(books)} книг в категории {category_url}.")
            return books

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка запроса при получении книг из категории {category_url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при получении книг из категории {category_url}: {e}")
            return []
            # Поиск через OPDS только через Tor
            books = self._search_via_opds(query, limit)
                
        except Exception as e:
            self.logger.error(f"Ошибка поиска на Флибусте через Tor: {e}")
        
        return books
    
    def browse_categories(self) -> List[Dict[str, Any]]:
        """Получить список доступных категорий/жанров через OPDS"""
        try:
            # Используем OPDS каталог для получения жанров
            opds_url = f"{self.base_url}/opds/genres"
            self.logger.info(f"Запрос жанров через OPDS: {opds_url}")
            
            response = self.session.get(opds_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Парсим XML ответ
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            categories = []
            entries = root.findall('.//atom:entry', ns)
            
            for entry in entries:
                title_elem = entry.find('atom:title', ns)
                if title_elem is not None:
                    category_name = title_elem.text
                    
                    # Получаем ссылку на категорию
                    links = entry.findall('atom:link', ns)
                    category_url = None
                    for link in links:

                        href = link.get('href')
                        if href:
                            category_url = f"{self.base_url}{href}"
                            break
                    
                    if category_name and category_url:
                        # Извлекаем ID категории из URL (если есть)
                        import re
                        category_id = category_name.lower().replace(' ', '_')
                        
                        categories.append({
                            'id': category_id,
                            'name': category_name,
                            'url': category_url
                        })
            
            self.logger.info(f"Найдено {len(categories)} категорий через OPDS")
            return categories
            
        except Exception as e:
            self.logger.error(f"Ошибка получения категорий через OPDS: {e}")
            return []
    
    def get_all_genres(self) -> List[Dict[str, Any]]:
        """Получить полный список всех жанров с HTML-страницы"""
        try:
            # Используем прямую ссылку на страницу со всеми жанрами
            genres_url = f"{self.base_url}/g"
            self.logger.info(f"Запрос всех жанров: {genres_url}")
            
            response = self.session.get(genres_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Парсим HTML ответ
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Находим все ссылки на жанры (содержат /g/ в href)
            genre_links = soup.find_all('a', href=True)
            genres = []
            
            for link in genre_links:
                href = link.get('href', '')
                if '/g/' in href and href != '/g':
                    genre_name = link.text.strip()
                    if genre_name:  # Проверяем, что название не пустое
                        # Формируем полный URL
                        if href.startswith('/'):
                            genre_url = f"{self.base_url}{href}"
                        else:

                            genre_url = href
                        
                        # Извлекаем ID жанра из URL
                        genre_id = href.split('/')[-1] if '/' in href else href
                        
                        genres.append({
                            'id': genre_id,
                            'name': genre_name,
                            'url': genre_url
                        })
            
            self.logger.info(f"Найдено {len(genres)} жанров через HTML-парсинг")
            return genres
            
        except Exception as e:
            self.logger.error(f"Ошибка получения всех жанров: {e}")
            return []
    
    def _clean_xml_content(self, content: bytes) -> bytes:
        """Очистка XML контента от HTML entities"""
        try:
            # Декодируем в строку
            text = content.decode('utf-8', errors='ignore')
            # Заменяем HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&mdash;', '—')
            text = text.replace('&ndash;', '–')
            text = text.replace('&laquo;', '«')
            text = text.replace('&raquo;', '»')
            text = text.replace('&hellip;', '…')
            # Кодируем обратно в байты
            return text.encode('utf-8')
        except Exception:
            return content
    
    def browse_books_by_category(self, category_url: str, sort_by_popularity: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
        self.logger.info(f"Начало обработки категории: {category_url} (лимит: {limit})")
        self.logger.debug(f"Сортировка по популярности: {sort_by_popularity}")
        """Получить книги из категории с сортировкой по популярности"""
        try:
            # Преобразуем URL в OPDS формат если нужно
            opds_url = category_url
            if '/g/' in category_url and '/opds' not in category_url:
                # Заменяем /g/ на /opds/g/ для получения OPDS-формата
                opds_url = category_url.replace('/g/', '/opds/g/')
            
            self.logger.info(f"Запрос к категории: {category_url}")
            self.logger.info(f"OPDS URL: {opds_url}")
            
            # Добавляем заголовки для получения OPDS-формата
            headers = {
                'Accept': 'application/atom+xml, application/xml, text/xml, */*',
                'User-Agent': 'OPDS-Client/1.0'
            }
            response = self.session.get(opds_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info(f"Получен ответ, размер: {len(response.content)} байт")
            self.logger.info(f"Content-Type: {response.headers.get('content-type', 'неизвестно')}")
            
            # Используем BeautifulSoup для более устойчивого парсинга
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем все entry элементы
            entries = soup.find_all('entry')
            self.logger.info(f"Найдено {len(entries)} записей entry")
            
            # Показываем первые несколько тегов для отладки
            all_tags = [tag.name for tag in soup.find_all() if tag.name]
            unique_tags = list(set(all_tags))
            self.logger.info(f"Найденные теги: {unique_tags[:10]}...")
            
            # Проверяем, содержит ли ответ книги или подкатегории
            if entries:
                first_entry = entries[0]
                self.logger.info(f"Анализируем первую запись...")
                # Если есть автор, значит это книги
                author_elem = first_entry.find('author')
                self.logger.info(f"Найден элемент author: {author_elem is not None}")
                if author_elem:
                    name_elem = author_elem.find('name')
                    self.logger.info(f"Найден элемент name в author: {name_elem is not None}")
                    if name_elem:
                        self.logger.info(f"Это книги, переходим к парсингу каталога")
                        # Это книги, парсим их
                        return self._get_books_from_catalog_bs(category_url, limit)
                
                self.logger.info(f"Это подкатегории, ищем первую доступную")
                # Это подкатегории, выбираем первую доступную
                for entry in entries:
                    links = entry.find_all('link')
                    for link in links:
                        href = link.get('href')
                        if href and not href.startswith('http'):
                            # Формируем полный URL
                            if href.startswith('/'):
                                full_href = f"{self.base_url}{href}"
                            else:
                                full_href = urljoin(opds_url, href)
                            
                            self.logger.info(f"Переходим в подкатегорию: {full_href}")
                            # Рекурсивно вызываем себя для подкатегории
                            subcategory_books = self.browse_books_by_category(full_href, sort_by_popularity, limit)
                            if subcategory_books:
                                return subcategory_books
                            break
                    if href:
                                subcategory_url = href if href.startswith('http') else f"{self.base_url}{href}"
                                # Рекурсивно получаем книги из подкатегории
                                books = self._get_books_from_catalog_bs(subcategory_url, limit)
                                if books:
                                    return books
            
            # Если ничего не найдено, возвращаем пустой список
            return books
            
        except Exception as e:
            self.logger.error(f"Ошибка получения книг из категории: {e}")
            return []
    
    def _get_books_from_catalog_bs(self, catalog_url: str, limit: int) -> List[Dict[str, Any]]:
        """Получить книги из каталога используя BeautifulSoup"""
        try:
            response = self.session.get(catalog_url, timeout=self.timeout)
            response.raise_for_status()
            
            self.logger.info(f"Получен ответ из каталога, размер: {len(response.content)} байт")
            self.logger.info(f"Content-Type: {response.headers.get('content-type', 'неизвестно')}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            books = []
            
            entries = soup.find_all('entry')
            self.logger.info(f"Найдено {len(entries)} записей entry в каталоге")
            
            # Показываем первые несколько тегов для отладки
            all_tags = [tag.name for tag in soup.find_all() if tag.name]
            unique_tags = list(set(all_tags))
            self.logger.info(f"Найденные теги в каталоге: {unique_tags[:15]}...")
            
            for i, entry in enumerate(entries[:limit]):
                self.logger.info(f"Обрабатываем запись {i+1}")
                book_data = self._parse_book_entry_bs(entry)
                if book_data:
                    self.logger.info(f"✅ Успешно обработана книга: {book_data.get('title', 'без названия')}")
                    books.append(book_data)
                else:
                    self.logger.warning(f"⚠️ Не удалось обработать запись {i+1}")
            
            self.logger.info(f"📊 Итого обработано книг: {len(books)}")
            return books
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения книг из каталога {catalog_url}: {e}")
            self.logger.debug(f"Подробности ошибки:", exc_info=True)
            return []
    
    def _get_books_from_catalog(self, catalog_url: str, limit: int) -> List[Dict[str, Any]]:
        """Получить книги из каталога"""
        try:
            response = self.session.get(catalog_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Очищаем XML от HTML entities
            cleaned_content = self._clean_xml_content(response.content)
            root = ET.fromstring(cleaned_content)
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
        self.logger.debug(f"🔍 Начинаем поиск через OPDS для запроса: '{query}' (лимит: {limit})")
        
        search_url = f"{self.opds_url}/search?searchTerm={query}"
        self.logger.debug(f"📡 Отправляем запрос к: {search_url}")
        
        response = self.session.get(search_url, timeout=self.timeout)
        response.raise_for_status()
        self.logger.debug(f"✅ Получен ответ, размер: {len(response.content)} байт")
        
        # Парсим OPDS XML
        root = ET.fromstring(response.content)
        books = []
        
        # Namespace для OPDS
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'opds': 'http://opds-spec.org/2010/catalog'
        }
        
        entries = root.findall('.//atom:entry', ns)
        self.logger.debug(f"📋 Найдено {len(entries)} записей в первоначальном ответе")
        
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
                            self.logger.debug(f"🔗 Найдена поисковая ссылка: {title_text} -> {href}")
                            break
        
        self.logger.debug(f"🔍 Найдено {len(search_links)} поисковых ссылок")
        
        # Если найдены поисковые ссылки, переходим по ним
        if search_links:
            self.logger.debug(f"🚀 Переходим по поисковым ссылкам...")
            for search_type, search_href in search_links:
                if len(books) >= limit:
                    self.logger.debug(f"⏹️ Достигнут лимит книг ({limit}), прекращаем поиск")

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
                    
                    self.logger.debug(f"🔗 Переходим по ссылке '{search_type}': {full_url}")
                    
                    # Получаем результаты поиска
                    search_response = self.session.get(full_url, timeout=self.timeout)
                    search_response.raise_for_status()
                    self.logger.debug(f"✅ Получен ответ от поисковой ссылки, размер: {len(search_response.content)} байт")
                    
                    # Парсим результаты
                    search_root = ET.fromstring(search_response.content)
                    search_entries = search_root.findall('.//atom:entry', ns)
                    self.logger.debug(f"📚 Найдено {len(search_entries)} книг в результатах поиска")
                    
                    for i, entry in enumerate(search_entries):
                        if len(books) >= limit:
                            self.logger.debug(f"⏹️ Достигнут лимит книг ({limit}), прекращаем парсинг")

                            break
                            
                        self.logger.debug(f"📖 Обрабатываем книгу {i+1}/{len(search_entries)}...")
                        book_data = self._parse_book_entry(entry, ns)
                        if book_data:
                            books.append(book_data)
                            self.logger.debug(f"✅ Книга добавлена: {book_data.get('title', 'Без названия')} - {book_data.get('author', 'Неизвестный автор')}")
                        else:
                            pass

                except Exception as e:
                    self.logger.error(f"❌ Ошибка при переходе по ссылке '{search_type}': {e}")

                    continue
        else:
            # Если это уже результаты поиска, парсим их напрямую
            for entry in entries[:limit]:
                book_data = self._parse_book_entry(entry, ns)
                if book_data:
                    books.append(book_data)
        
        return books
    
    def _parse_book_entry_bs(self, entry) -> Optional[Dict[str, Any]]:
        """Парсинг одной записи книги из OPDS используя BeautifulSoup"""
        try:
            title_elem = entry.find('title')
            author_elem = entry.find('author')
            summary_elem = entry.find('summary')
            
            self.logger.debug(f"Парсинг записи:")
            self.logger.debug(f"📖 Начало парсинга записи книги")
            self.logger.debug(f"  📌 Заголовок: {title_elem.get_text().strip() if title_elem else 'НЕТ'}")
            self.logger.debug(f"  ✍️ Автор: {author_elem is not None}")
            self.logger.debug(f"  📝 Описание: {summary_elem is not None}")
            
            # Пропускаем служебные записи
            if title_elem:
                title_text = title_elem.get_text().strip()
                self.logger.debug(f"  📖 Текст заголовка: {title_text}")
                if any(skip_word in title_text for skip_word in ['Поиск', 'Search', 'Каталог', 'Catalog']):
                    self.logger.debug(f"  ⏭️ Пропускаем служебную запись")

                    return None
            
            # Проверяем, есть ли ссылки для скачивания (acquisition) - это отличает книги от категорий
            has_download_links = False
            links = entry.find_all('link')
            self.logger.debug(f"  🔗 Найдено {len(links)} ссылок в записи")
            for link in links:
                rel = link.get('rel')
                href = link.get('href')
                type_attr = link.get('type')

                # Обрабатываем rel - может быть строкой, списком или AttributeValueList
                if rel:
                    if isinstance(rel, list):
                        rel_values = [r.strip() for r in rel]
                    elif hasattr(rel, '__iter__') and not isinstance(rel, str):
                        # Обрабатываем AttributeValueList и другие итерируемые объекты
                        rel_values = [str(r).strip() for r in rel]
                    else:
                        rel_values = [str(rel).strip()]
                    
                    for rel_val in rel_values:
                        if rel_val in ['http://opds-spec.org/acquisition', 'http://opds-spec.org/acquisition/open-access']:
                            has_download_links = True
                            break
                    if has_download_links:
                        break
            
            self.logger.debug(f"  📥 Ссылки для скачивания: {'есть' if has_download_links else 'нет'}")
            # Если нет ссылок для скачивания, это скорее всего категория, а не книга
            if not has_download_links:
                self.logger.debug(f"  ⏭️ Нет ссылок для скачивания, пропускаем запись")

                return None
            
            # Извлекаем основную информацию
            title = title_elem.get_text().strip() if title_elem else 'Без названия'
            author = ''
            if author_elem:
                name_elem = author_elem.find('name')
                if name_elem:
                    author = name_elem.get_text().strip()
            
            description = summary_elem.get_text().strip() if summary_elem else ''
            
            # Извлекаем ссылки для скачивания
            download_links = {}
            for link in entry.find_all('link'):
                rel = link.get('rel')
                # Обрабатываем rel - может быть строкой или списком
                if rel:
                    if isinstance(rel, list):
                        rel_values = [r.strip() for r in rel]
                    else:
                        rel_values = [rel.strip()]
                    
                    for rel_val in rel_values:
                        if rel_val in ['http://opds-spec.org/acquisition', 'http://opds-spec.org/acquisition/open-access']:
                            href = link.get('href')
                            mime_type = link.get('type', '')
                            
                            if href:
                                # Формируем полный URL
                                if href.startswith('/'):
                                    full_url = f"{self.base_url}{href}"
                                else:
                                    full_url = href
                                
                                # Определяем формат файла
                                file_format = self._extract_format_from_type(mime_type)
                                
                                download_links[file_format] = {
                                    'url': full_url,
                                    'type': mime_type
                                }
                            break
            
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
            self.logger.error(f"Ошибка парсинга записи OPDS: {e}")
            return None
    
    def _parse_book_entry(self, entry, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Парсинг одной записи книги из OPDS"""
        try:
            title = entry.find('atom:title', ns)
            author = entry.find('atom:author/atom:name', ns)
            summary = entry.find('atom:summary', ns)
            updated = entry.find('atom:updated', ns)
            
            title_text = title.text.strip() if title is not None and title.text else "Без названия"
            author_text = author.text.strip() if author is not None and author.text else "Неизвестный автор"
            
            self.logger.debug(f"  🔍 Парсим запись: '{title_text}' - {author_text}")
            
            # Пропускаем служебные записи
            if title is not None:
                self.logger.debug(f"  ⏭️ Пропускаем служебную запись: {title_text}")
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
            
            book_data = {
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
            
            print(f"  ✅ Успешно спарсили книгу: '{book_data['title']}' - {book_data['author']} (ID: {book_id})")
            return book_data
            
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
            title = book_data.get('title', 'Неизвестная книга')
            author = book_data.get('author', 'Неизвестный автор')
            print(f"📥 Начинаем скачивание книги: '{title}' - {author}")
            
            download_links = book_data.get('download_links', {})
            
            if not download_links:
                # Если нет прямых ссылок, пробуем получить их через ID книги
                source_id = book_data.get('source_id')
                if source_id:
                    download_links = self._get_download_links_by_id(source_id)
            
            # Преобразуем словарь ссылок в список, если это словарь
            if isinstance(download_links, dict):
                links_list = []
                for format_key, link_data in download_links.items():
                    if isinstance(link_data, dict):
                        link_data['format'] = format_key
                        links_list.append(link_data)
                download_links = links_list
            
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
            
            format_name = preferred_link.get('format', 'неизвестный')
            print(f"🔗 Скачиваем файл в формате {format_name} с URL: {download_url}")
            self.logger.info(f"Скачивание книги: {book_data.get('title')} в формате {format_name}")
            
            response = self.session.get(download_url, timeout=self.timeout * 2, stream=True)
            response.raise_for_status()
            print(f"✅ HTTP запрос успешен, статус: {response.status_code}")
            
            # Проверяем размер файла
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > EXTERNAL_SOURCES_CONFIG['max_file_size']:
                self.logger.error(f"Файл слишком большой: {content_length} байт")
                return None
            
            # Получаем содержимое
            print(f"📦 Загружаем содержимое файла...")
            content = b''
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                total_size += len(chunk)
                if len(content) > EXTERNAL_SOURCES_CONFIG['max_file_size']:
                    self.logger.error("Превышен максимальный размер файла")
                    return None
            
            print(f"✅ Файл загружен, размер: {total_size} байт")
            
            # Определяем кодировку и декодируем
            print(f"🔄 Обрабатываем содержимое файла в формате {format_name}...")
            result = self._decode_content(content, preferred_link.get('format', 'fb2'))
            
            if result:
                print(f"✅ Книга '{title}' успешно обработана и готова к использованию")
            else:
                print(f"❌ Ошибка обработки книги '{title}'")
                
            return result
            
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
    
    def get_book_description(self, book_id: str) -> Optional[str]:
        """Получение аннотации книги по ID"""
        try:
            book_url = f"{self.base_url}/b/{book_id}"
            response = self.session.get(book_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем раздел с аннотацией
            annotation_header = soup.find('h2', string='Аннотация')
            if annotation_header:
                # Находим следующий элемент после заголовка "Аннотация"
                annotation_content = []
                current_element = annotation_header.next_sibling
                
                while current_element:
                    if hasattr(current_element, 'name'):
                        # Если это тег
                        if current_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            # Если встретили другой заголовок, прекращаем
                            break
                        elif current_element.name == 'p':
                            # Добавляем текст параграфа
                            text = current_element.get_text(strip=True)
                            if text and text != '&nbsp;':
                                annotation_content.append(text)
                        elif current_element.name == 'br':
                            # Пропускаем переносы строк
                            pass
                    else:
                        # Если это текстовый узел
                        text = str(current_element).strip()
                        if text and text != '&nbsp;':
                            annotation_content.append(text)
                    
                    current_element = current_element.next_sibling
                
                if annotation_content:
                    return '\n\n'.join(annotation_content)
            
            self.logger.info(f"Аннотация для книги {book_id} не найдена")
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения аннотации для книги {book_id}: {e}")
            return None
    
    def _decode_content(self, content: bytes, file_format: str) -> str:
        """Декодирование содержимого файла"""
        try:
            print(f"🔍 Анализируем тип файла: {file_format}")
            
            # Проверяем, является ли файл ZIP архивом
            if self._is_zip_archive(content):
                print(f"📦 Обнаружен ZIP архив, начинаем разархивирование...")
                return self._extract_from_zip(content, file_format)
            else:
                print(f"📄 Обычный файл, начинаем декодирование...")
            
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
                print(f"📋 Файлы в архиве: {file_list}")
                
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
                    print(f"🎯 Найден целевой файл: {target_file}")
                    
                    # Извлекаем файл
                    print(f"📤 Извлекаем файл из архива...")
                    extracted_content = zip_file.read(target_file)
                    print(f"✅ Файл извлечен, размер: {len(extracted_content)} байт")
                    
                    # Определяем формат по расширению файла
                    file_format = expected_format
                    for fmt, extensions in format_extensions.items():
                        if any(target_file.lower().endswith(ext) for ext in extensions):
                            file_format = fmt
                            break
                    
                    print(f"📝 Определен формат файла: {file_format}")
                    self.logger.info(f"Извлечен файл {target_file} из архива, формат: {file_format}")
                    
                    # Рекурсивно обрабатываем извлеченный файл
                    print(f"🔄 Рекурсивно обрабатываем извлеченный файл...")
                    return self._decode_content(extracted_content, file_format)
                else:
                    print(f"❌ В архиве не найдено подходящих файлов")
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
    
    def get_book_description(self, book_id: str) -> Optional[str]:
        """Получение аннотации книги из Flibusta"""
        try:
            return self.flibusta.get_book_description(book_id)
        except Exception as e:
            print(f"Ошибка получения аннотации книги: {e}")
            return None
    
    def get_book_content(self, book_data: Dict[str, Any], format_type: str = 'fb2') -> Optional[str]:
        """Получение содержимого книги из внешнего источника"""
        try:
            # Используем уже имеющиеся данные книги
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
            # Если передан URL, используем его напрямую
            if category.startswith('http'):
                return self.flibusta.browse_books_by_category(category, sort_by_popularity=True, limit=limit)
            
            # Иначе ищем категорию по названию
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
    return sources.get_book_content(book_data, download_format)