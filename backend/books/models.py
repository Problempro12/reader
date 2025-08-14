from django.db import models
from django.conf import settings

class Author(models.Model):
    """Author model"""
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    photo_url = models.ImageField(upload_to='authors/', null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    """Book model"""
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField()
    genre = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(null=True, blank=True)
    vote_count = models.IntegerField(default=0)
    is_book_of_week = models.BooleanField(default=False)
    gutenberg_id = models.IntegerField(null=True, blank=True, unique=True)
    source_id = models.CharField(max_length=255, null=True, blank=True)  # ID книги во внешнем источнике (Флибуста, LibGen)
    source_type = models.CharField(max_length=50, null=True, blank=True)  # Тип источника: flibusta, libgen, google_books
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class UserBook(models.Model):
    """User's book with status"""
    class Status(models.TextChoices):
        READING = 'reading', 'Reading'
        COMPLETED = 'completed', 'Completed'
        PLANNED = 'planned', 'Planned'
        DROPPED = 'dropped', 'Dropped'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='user_books')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    rating = models.IntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'book')
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

class ReadingProgress(models.Model):
    """Reading progress for a user book"""
    user_book = models.ForeignKey(UserBook, on_delete=models.CASCADE, related_name='progress_marks')
    position = models.IntegerField()  # Position in the text (character position)
    current_page = models.IntegerField(default=1)  # Current page number
    total_pages = models.IntegerField(default=1)  # Total pages in book
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_book.user.username} - {self.user_book.book.title} - Page: {self.current_page}/{self.total_pages}"
    
    @property
    def progress_percentage(self):
        """Calculate reading progress as percentage"""
        if self.total_pages <= 0:
            return 0
        return min(100, (self.current_page / self.total_pages) * 100)

class BookVote(models.Model):
    """User vote for a book"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_votes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'book')
    
    def __str__(self):
        return f"{self.user.username} voted for {self.book.title}"

class WeeklyBook(models.Model):
    """Book of the week model"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='weekly_selections')
    week_start = models.DateField()
    week_end = models.DateField()
    votes_at_selection = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('week_start', 'week_end')
        ordering = ['-week_start']
    
    def __str__(self):
        return f"Book of the week {self.week_start} - {self.week_end}: {self.book.title}"
