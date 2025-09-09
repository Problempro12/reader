import os
import django
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.reader.settings')

# Инициализируем Django
django.setup()

from backend.books.external_sources import search_external_books, import_book_from_external_source

# Шаг 1: ищем книги
query = "Лукьяненко"
print(f"Ищем книги по запросу: '{query}' на Flibusta через Tor...")
results = search_external_books(query, sources=["flibusta"], use_tor=True, limit=5)
print(f"Результаты поиска: {results}")
books = results.get("flibusta", [])

print(f"Найдено {len(books)} книг")

# Шаг 2: импортируем первую книгу
if books:
    book_data = books[0]
    print(f"Импортируем первую книгу: {book_data.get('title', 'N/A')} - {book_data.get('author', 'N/A')}")
    content = import_book_from_external_source(book_data, source="flibusta", download_format="fb2", use_tor=True)
    if content:
        file_name = f"{book_data.get('author', 'unknown').replace(' ', '_')}_{book_data.get('title', 'unknown').replace(' ', '_')}.fb2"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Книга сохранена: {book_data.get('title', 'N/A')} - {book_data.get('author', 'N/A')} в файл {file_name}")
    else:
        print(f"❌ Не удалось импортировать книгу: {book_data.get('title', 'N/A')}")
else:
    print("Книги не найдены.")