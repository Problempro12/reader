import requests
from datetime import datetime
from .models import Book, Author
import re

# Google Books импорт удален - используем только Флибусту

def get_real_book_content_from_external_sources(book_title, author_name):
    """
    Получает реальное содержимое книги из внешних источников (только Флибуста)
    """
    try:
        from .external_sources import ExternalBookSources
        
        # Создаем клиент для работы с внешними источниками
        sources = ExternalBookSources()
        
        # Ищем книгу в Флибусте
        search_results = sources.search_flibusta(f"{book_title} {author_name}", limit=1)
        
        if search_results:
            book_data = search_results[0]
            # Пытаемся загрузить содержимое
            content = sources.get_book_content(book_data, 'fb2')
            
            if content and len(content.strip()) > 100:  # Проверяем что контент не пустой
                return format_book_content(book_title, author_name, content)
    
    except Exception as e:
        print(f"Ошибка при получении книги из внешних источников: {e}")
    
    # Если не удалось получить реальное содержимое, возвращаем заглушку
    return get_demo_book_content(book_title, author_name)

def format_book_content(title, author, content):
    """
    Форматирует содержимое книги для отображения
    """
    if not content or len(content.strip()) < 50:
        return get_demo_book_content(title, author)
    
    formatted_content = f"""# {title}

**Автор:** {author}

---

{content}

---

*Источник: Флибуста*"""
    
    return formatted_content

def get_demo_book_content(book_title, author_name):
    """
    Возвращает демонстрационное содержимое, если реальный текст недоступен
    """
    return f"""# {book_title}

**Автор:** {author_name}

---

## Демонстрационное содержимое

К сожалению, полный текст этой книги временно недоступен для автоматической загрузки.

### Что можно сделать:

1. **Поиск в других источниках** - попробуйте альтернативные библиотеки
2. **Покупка лицензированной версии** - для современных произведений под авторским правом
3. **Обратитесь к администратору** - для добавления книги в библиотеку

### Доступные форматы:

- FB2 (FictionBook)
- EPUB (Electronic Publication)
- TXT (Plain Text)
- PDF (Portable Document Format)

---

*Примечание: Это демонстрационная читалка. Полное содержимое будет доступно после загрузки из источников.*"""

def get_book_content_from_external_sources(book_title, author_name):
    """Получение содержимого книги из внешних источников"""
    return get_real_book_content_from_external_sources(book_title, author_name)