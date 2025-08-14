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

def paginate_book_content(content: str, page: int = 1, words_per_page: int = 300) -> dict:
    """
    Разделяет содержимое книги на страницы
    
    Args:
        content: Полный текст книги
        page: Номер запрашиваемой страницы (начиная с 1)
        words_per_page: Количество слов на странице
    
    Returns:
        Dict с данными о странице
    """
    if not content or not content.strip():
        return {
            'current_page': 1,
            'total_pages': 1,
            'content': 'Содержимое книги недоступно.',
            'has_next': False,
            'has_previous': False
        }
    
    # Очищаем контент от лишних пробелов и переносов
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Разбиваем на слова
    words = content.split()
    total_words = len(words)
    
    if total_words == 0:
        return {
            'current_page': 1,
            'total_pages': 1,
            'content': 'Содержимое книги недоступно.',
            'has_next': False,
            'has_previous': False
        }
    
    # Вычисляем общее количество страниц
    total_pages = max(1, (total_words + words_per_page - 1) // words_per_page)
    
    # Проверяем корректность номера страницы
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # Вычисляем индексы для текущей страницы
    start_word_index = (page - 1) * words_per_page
    end_word_index = min(start_word_index + words_per_page, total_words)
    
    # Получаем слова для текущей страницы
    page_words = words[start_word_index:end_word_index]
    page_content = ' '.join(page_words)
    
    # Улучшаем форматирование текста
    page_content = format_page_content(page_content)
    
    return {
        'current_page': page,
        'total_pages': total_pages,
        'content': page_content,
        'has_next': page < total_pages,
        'has_previous': page > 1
    }

def format_page_content(content: str) -> str:
    """
    Улучшает форматирование текста страницы
    
    Args:
        content: Текст страницы
    
    Returns:
        Отформатированный текст
    """
    if not content:
        return content
    
    # Добавляем переносы строк после точек (если за ними идет заглавная буква)
    content = re.sub(r'\. ([А-ЯA-Z])', r'.\n\n\1', content)
    
    # Добавляем переносы для диалогов
    content = re.sub(r'([.!?]) — ', r'\1\n\n— ', content)
    content = re.sub(r'^— ', r'— ', content, flags=re.MULTILINE)
    
    # Убираем лишние пробелы
    content = re.sub(r' +', ' ', content)
    
    # Убираем лишние переносы строк (больше двух подряд)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def calculate_reading_position(content: str, page: int, words_per_page: int = 300) -> int:
    """
    Вычисляет позицию в тексте (в символах) для заданной страницы
    
    Args:
        content: Полный текст книги
        page: Номер страницы
        words_per_page: Количество слов на странице
    
    Returns:
        Позиция в символах
    """
    if not content or page < 1:
        return 0
    
    words = content.split()
    start_word_index = (page - 1) * words_per_page
    
    if start_word_index >= len(words):
        return len(content)
    
    # Находим позицию первого слова на странице в исходном тексте
    words_before = words[:start_word_index]
    chars_before = sum(len(word) + 1 for word in words_before)  # +1 для пробела
    
    return max(0, chars_before - 1)  # -1 чтобы убрать последний пробел

def get_page_from_position(content: str, position: int, words_per_page: int = 300) -> int:
    """
    Определяет номер страницы по позиции в тексте
    
    Args:
        content: Полный текст книги
        position: Позиция в символах
        words_per_page: Количество слов на странице
    
    Returns:
        Номер страницы
    """
    if not content or position <= 0:
        return 1
    
    # Получаем текст до указанной позиции
    text_before = content[:position]
    words_before = len(text_before.split())
    
    # Вычисляем номер страницы
    page = (words_before // words_per_page) + 1
    
    return max(1, page)