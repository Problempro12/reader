import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional

# Добавляем путь к корневой директории проекта
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Загружаем переменные окружения
load_dotenv(root_dir / '.env')

from books.google_books_api import GoogleBooksAPI
from prisma import Prisma

# Создаем экземпляр API
api = GoogleBooksAPI()

# Список категорий для импорта
CATEGORIES = ['fiction', 'fantasy']

# Создаем базовые записи для жанров и возрастных категорий
async def create_base_records(prisma_client):
    print("\nСоздание базовых записей...")
    
    genre = await prisma_client.genre.find_first(
        where={'name': 'Художественная литература'}
    )
    if not genre:
        print("Создаем жанр 'Художественная литература'")
        genre = await prisma_client.genre.create(
            data={'name': 'Художественная литература'}
        )
    print(f"Жанр: {json.dumps(genre.model_dump(), indent=2, ensure_ascii=False)}")
    
    age_category = await prisma_client.agecategory.find_first(
        where={'name': 'Для взрослых'}
    )
    if not age_category:
        print("Создаем возрастную категорию 'Для взрослых'")
        age_category = await prisma_client.agecategory.create(
            data={'name': 'Для взрослых'}
        )
    print(f"Возрастная категория: {json.dumps(age_category.model_dump(), indent=2, ensure_ascii=False)}")
    
    return genre, age_category

async def ensure_genre(prisma_client, genre_name: str, categories: List[str], default_genre_id: int) -> int:
    """
    Проверяет существование жанра по ID или имени, создаёт новый жанр, если не найден.
    Возвращает ID жанра.
    """
    # Сначала пытаемся найти жанр по ID из map_google_genre_to_our_genre
    genre_id = api.map_google_genre_to_our_genre(categories)
    if genre_id:
        genre = await prisma_client.genre.find_first(where={'id': genre_id})
        if genre:
            print(f"Найден жанр: {genre.name} (id: {genre.id})")
            return genre.id

    # Если ID не задан или жанр не найден, пытаемся найти по имени
    genre_name = genre_name or (categories[0] if categories else 'Художественная литература')
    genre = await prisma_client.genre.find_first(where={'name': genre_name})
    if genre:
        print(f"Найден жанр по имени: {genre.name} (id: {genre.id})")
        return genre.id

    # Создаём новый жанр
    print(f"Создаём новый жанр: {genre_name}")
    new_genre = await prisma_client.genre.create(data={'name': genre_name})
    print(f"Создан жанр: {json.dumps(new_genre.model_dump(), indent=2, ensure_ascii=False)}")
    return new_genre.id

async def import_books():
    print("\nНачинаем импорт книг...\n")
    
    prisma_client = Prisma()
    await prisma_client.connect()
    
    try:
        genre, age_category = await create_base_records(prisma_client)
        
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        
        for category in CATEGORIES:
            print(f"\nПоиск книг по запросу: subject:{category}")
            
            try:
                # Получаем список книг
                books = await api.search_books(f"subject:{category}", max_results=10)
                print(f"Найдено {len(books)} книг для категории {category}")
                
                for google_book in books:
                    try:
                        book_data = await api.get_book_details(google_book.get('id'))
                        if not book_data:
                            continue
                        
                        print(f"\nПолучены детали книги {google_book.get('id')}: {list(book_data.keys())}")
                        
                        volume_info = book_data.get('volumeInfo', {})
                        title = volume_info.get('title')
                        authors = volume_info.get('authors', [])
                        categories = volume_info.get('categories', [])
                        
                        if not title or not authors:
                            continue
                        
                        author = authors[0]
                        
                        # Проверяем, существует ли уже такая книга
                        existing_book = await prisma_client.book.find_first(
                            where={
                                'title': title,
                                'author': author
                            }
                        )
                        
                        if existing_book:
                            print(f"Книга {title} уже существует")
                            continue
                        
                        # Получаем или создаём жанр
                        genre_id = await ensure_genre(prisma_client, categories[0] if categories else None, categories, genre.id)
                        print(f"Genre ID для книги {title}: {genre_id}")
                        
                        # Подготавливаем данные для создания книги
                        book_data = {
                            'title': title,
                            'author': author,
                            'genreId': genre_id,  # Прямое указание ID жанра
                            'ageCategoryId': age_category.id,  # Прямое указание ID возрастной категории
                            'isPremium': False,
                            'rating': 0.0,
                            'rating_count': 0  # Используем snake_case как в схеме
                        }

                        print(f"\nПопытка создания книги с данными:")
                        print(json.dumps(book_data, indent=2, ensure_ascii=False))

                        try:
                            book = await prisma_client.book.create(data=book_data)
                            print(f"Импортирована книга: {book.title}")
                            total_imported += 1
                        except Exception as e:
                            print(f"Ошибка при создании книги {title}: {e}")
                            print(f"Тип ошибки: {type(e)}")
                            print(f"Детали ошибки: {str(e)}")
                            print(f"Данные, которые вызвали ошибку:")
                            print(json.dumps(book_data, indent=2, ensure_ascii=False))
                            total_errors += 1
                            continue
                        
                    except Exception as e:
                        print(f"Ошибка при создании книги {title}: {e}")
                        print(f"Тип ошибки: {type(e)}")
                        print(f"Детали ошибки: {str(e)}")
                        total_errors += 1
                        continue
                    
            except Exception as e:
                print(f"Ошибка при обработке категории {category}: {e}")
                total_errors += 1
                continue
        
        print(f"\nИмпорт завершен:")
        print(f"Импортировано книг: {total_imported}")
        print(f"Пропущено книг: {total_skipped}")
        print(f"Ошибок: {total_errors}")
        
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(import_books())