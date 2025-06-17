import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
from tqdm import tqdm

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
CATEGORIES = ['fiction', 'fantasy', 'science fiction', 'mystery', 'romance']

async def create_base_records(prisma_client):
    print("\nСоздание базовых записей...")
    
    genre = await prisma_client.genre.find_first(where={'name': 'Художественная литература'})
    if not genre:
        print("Создаем жанр 'Художественная литература'")
        genre = await prisma_client.genre.create(data={'name': 'Художественная литература'})
    print(f"Жанр: {json.dumps(genre.model_dump(), indent=2, ensure_ascii=False)}")
    
    age_category = await prisma_client.agecategory.find_first(where={'name': 'Для взрослых'})
    if not age_category:
        print("Создаем возрастную категорию 'Для взрослых'")
        age_category = await prisma_client.agecategory.create(data={'name': 'Для взрослых'})
    print(f"Возрастная категория: {json.dumps(age_category.model_dump(), indent=2, ensure_ascii=False)}")
    
    return genre, age_category

async def ensure_author(prisma_client, author_name: str) -> int:
    # Поиск автора
    res = await prisma_client.execute_raw('SELECT id FROM "Author" WHERE name = $1', author_name)
    if res:
        print(f"Найден автор: {author_name} (id: {res})")
        return res
    # Создание автора
    insert = await prisma_client.execute_raw('INSERT INTO "Author" (name, "createdAt", "updatedAt") VALUES ($1, NOW(), NOW()) RETURNING id', author_name)
    print(f"Создан автор: {author_name} (id: {insert})")
    return insert

async def ensure_genre(prisma_client, genre_name: str, categories: list, default_genre_id: int) -> int:
    genre_id = api.map_google_genre_to_our_genre(categories)
    if genre_id:
        res = await prisma_client.execute_raw('SELECT id FROM "Genre" WHERE id = $1', genre_id)
        if res:
            print(f"Найден жанр: (id: {res})")
            return res
    genre_name = genre_name or (categories[0] if categories else 'Художественная литература')
    res = await prisma_client.execute_raw('SELECT id FROM "Genre" WHERE name = $1', genre_name)
    if res:
        print(f"Найден жанр по имени: {genre_name} (id: {res})")
        return res
    insert = await prisma_client.execute_raw('INSERT INTO "Genre" (name) VALUES ($1) RETURNING id', genre_name)
    print(f"Создан жанр: {genre_name} (id: {insert})")
    return insert

async def create_book(prisma_client, book_data: dict) -> int:
    # Проверка существования книги
    res = await prisma_client.execute_raw('SELECT id FROM "Book" WHERE title = $1 AND "authorId" = $2', book_data['title'], book_data['authorId'])
    if res:
        print(f"Книга {book_data['title']} уже существует")
        return res
    # Вставка книги
    insert = await prisma_client.execute_raw('''
        INSERT INTO "Book" (
            title, description, "coverUrl", "externalId", rating, rating_count, 
            "authorId", "genreId", "ageCategoryId", "isPremium", "createdAt", "updatedAt",
            isbn, year, series, translator, volume, "copyrightHolder"
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW(), $11, $12, $13, $14, $15, $16
        ) RETURNING id
    ''',
        book_data['title'],
        book_data.get('description', ''),
        book_data.get('coverUrl', ''),
        book_data.get('externalId', ''),
        book_data.get('rating', 0.0),
        book_data.get('rating_count', 0),
        book_data['authorId'],
        book_data['genreId'],
        book_data['ageCategoryId'],
        book_data.get('isPremium', False),
        book_data.get('isbn', ''),
        book_data.get('year', ''),
        book_data.get('series', ''),
        book_data.get('translator', ''),
        book_data.get('volume', ''),
        book_data.get('copyrightHolder', '')
    )
    print(f"Импортирована книга: {book_data['title']} (id: {insert})")
    return insert

async def import_book_by_isbn(prisma_client, isbn: str) -> bool:
    try:
        book_data = await api.get_book_by_isbn(isbn)
        if not book_data:
            print(f"Книга с ISBN {isbn} не найдена")
            return False
        volume_info = book_data.get('volumeInfo', {})
        title = volume_info.get('title')
        authors = volume_info.get('authors', [])
        categories = volume_info.get('categories', [])
        if not title or not authors:
            print(f"Недостаточно данных для книги с ISBN {isbn}")
            return False
        author_id = await ensure_author(prisma_client, authors[0])
        existing_book = await prisma_client.book.find_first(where={
            'title': title,
            'authorId': author_id
        })
        if existing_book:
            print(f"Книга {title} уже существует")
            return False
        genre_id = await ensure_genre(prisma_client, categories[0] if categories else None, categories, 1)
        book_create_data = {
            "title": title,
            "description": volume_info.get('description', ''),
            "coverUrl": volume_info.get('imageLinks', {}).get('thumbnail', ''),
            "externalId": book_data.get('id', ''),
            "rating": volume_info.get('averageRating', 0.0),
            "rating_count": volume_info.get('ratingsCount', 0),
            "pageCount": volume_info.get('pageCount', 0),
            "publishedDate": datetime.strptime(volume_info.get('publishedDate', ''), '%Y-%m-%d') if volume_info.get('publishedDate') else None,
            "publisher": volume_info.get('publisher', ''),
            "language": volume_info.get('language', ''),
            "isbn": isbn,
            "authorId": author_id,
            "genreId": genre_id,
            "ageCategoryId": 1,
            "isPremium": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        book = await prisma_client.book.create(data=book_create_data)
        print(f"Импортирована книга: {book.title}")
        return True
    except Exception as e:
        print(f"Ошибка при импорте книги с ISBN {isbn}: {e}")
        return False

async def import_books():
    print("\nНачинаем импорт книг...\n")
    prisma_client = Prisma()
    await prisma_client.connect()
    try:
        # Создаем базовые записи (жанр и возрастную категорию)
        genre, age_category = await create_base_records(prisma_client)
        total_imported = 0
        total_skipped = 0
        total_errors = 0
        for category in tqdm(CATEGORIES, desc="Импорт категорий"):
            print(f"\nПоиск книг по запросу: subject:{category}")
            books = await api.search_books(f"subject:{category}", max_results=10)
            print(f"Найдено {len(books)} книг для категории {category}")
            for google_book in tqdm(books, desc=f"Импорт книг категории {category}"):
                try:
                    book_data = await api.get_book_details(google_book.get('id'))
                    if not book_data:
                        continue
                    volume_info = book_data.get('volumeInfo', {})
                    title = volume_info.get('title')
                    authors = volume_info.get('authors', [])
                    categories = volume_info.get('categories', [])
                    if not title or not authors:
                        continue
                    author_name = authors[0]
                    author_id = await ensure_author(prisma_client, author_name)
                    genre_id = await ensure_genre(prisma_client, categories[0] if categories else None, categories, genre.id)
                    
                    # Обработка даты публикации
                    published_date = volume_info.get('publishedDate', '')
                    year = None
                    if published_date:
                        try:
                            # Пробуем разные форматы даты
                            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                                try:
                                    year = datetime.strptime(published_date, fmt).year
                                    break
                                except ValueError:
                                    continue
                        except Exception:
                            pass
                    
                    book_create_data = {
                        "title": title,
                        "description": volume_info.get('description', ''),
                        "coverUrl": volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        "externalId": book_data.get('id', ''),
                        "rating": volume_info.get('averageRating', 0.0),
                        "rating_count": volume_info.get('ratingsCount', 0),
                        "authorId": author_id,
                        "genreId": genre_id,
                        "ageCategoryId": age_category.id,
                        "isPremium": False,
                        "isbn": next((identifier.get('identifier') for identifier in volume_info.get('industryIdentifiers', []) if identifier.get('type') == 'ISBN_13'), None),
                        "year": str(year) if year else '',
                        "series": volume_info.get('series', ''),
                        "translator": volume_info.get('translator', ''),
                        "volume": volume_info.get('volume', ''),
                        "copyrightHolder": volume_info.get('publisher', '')
                    }
                    book_id = await create_book(prisma_client, book_create_data)
                    if book_id:
                        total_imported += 1
                    else:
                        total_skipped += 1
                except Exception as e:
                    print(f"Ошибка при обработке книги: {e}")
                    total_errors += 1
                    continue
        print(f"\nИмпорт завершен:")
        print(f"Успешно импортировано: {total_imported}")
        print(f"Пропущено: {total_skipped}")
        print(f"Ошибок: {total_errors}")
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(import_books())
    asyncio.run(test_create_minimal_book())
    asyncio.run(test_create_minimal_book())