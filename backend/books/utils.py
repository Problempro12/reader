import requests
from datetime import datetime
from .models import Book, Author

# TODO: Replace with your actual Google Books API Key
GOOGLE_BOOKS_API_KEY = "AIzaSyDuGTLUy05d8pBo6sWuXwdsX8NnUZxhWdg"

def import_books_from_google_books(query):
    if not GOOGLE_BOOKS_API_KEY or GOOGLE_BOOKS_API_KEY == "YOUR_GOOGLE_BOOKS_API_KEY":
        return {"error": "Google Books API Key is not configured. Please set GOOGLE_BOOKS_API_KEY in backend/books/utils.py"}

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        imported_count = 0
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            title = volume_info.get('title')
            authors = volume_info.get('authors', [])
            description = volume_info.get('description')
            published_date = volume_info.get('publishedDate')

            if title and authors:
                author_name = authors[0] # Taking the first author for simplicity
                author, created = Author.objects.get_or_create(name=author_name)

                # Parse publication date
                parsed_date = None
                if published_date:
                    try:
                        # Try different date formats
                        if len(published_date) == 4:  # Year only
                            parsed_date = datetime.strptime(published_date, '%Y').date()
                        elif len(published_date) == 7:  # Year-Month
                            parsed_date = datetime.strptime(published_date, '%Y-%m').date()
                        elif len(published_date) == 10:  # Full date
                            parsed_date = datetime.strptime(published_date, '%Y-%m-%d').date()
                    except ValueError:
                        # If parsing fails, leave as None
                        parsed_date = None

                # Get cover image URL
                cover_url = None
                image_links = volume_info.get('imageLinks', {})
                if image_links:
                    # Try to get the highest quality image available
                    cover_url = (image_links.get('extraLarge') or 
                               image_links.get('large') or 
                               image_links.get('medium') or 
                               image_links.get('small') or 
                               image_links.get('thumbnail'))
                    
                    # Ensure high quality by using zoom=0
                    if cover_url and 'zoom=1' in cover_url:
                        cover_url = cover_url.replace('zoom=1', 'zoom=0')
                    
                    # Convert HTTP to HTTPS to avoid mixed content issues
                    if cover_url and cover_url.startswith('http://'):
                        cover_url = cover_url.replace('http://', 'https://')

                try:
                    book, created = Book.objects.get_or_create(
                        title=title,
                        author=author,
                        defaults={
                            'description': description or '',
                            'content': description or 'Содержимое книги будет добавлено позже.',
                            'published_date': parsed_date,
                            'cover_url': cover_url
                        }
                    )
                    if created:
                        imported_count += 1
                except Exception as e:
                    print(f"Error creating book '{title}': {e}")
                    continue

        return {"status": f"Successfully imported {imported_count} books from Google Books.", "query": query}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data from Google Books API: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred during import: {e}"}