from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GenreBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class GenreCreate(GenreBase):
    pass

class Genre(GenreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgeCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

class AgeCategoryCreate(AgeCategoryBase):
    pass

class AgeCategory(AgeCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BookBase(BaseModel):
    title: str
    author_id: int
    description: Optional[str] = None
    cover_url: Optional[str] = None
    external_id: Optional[str] = None
    age_category_id: int
    genre_id: int
    is_premium: bool = False
    litres_rating: Optional[float] = None
    litres_rating_count: Optional[int] = None
    series: Optional[str] = None
    translator: Optional[str] = None
    volume: Optional[str] = None
    year: Optional[str] = None
    isbn: Optional[str] = None
    copyright_holder: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    rating: float = 0.0
    rating_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBookBase(BaseModel):
    user_id: int
    book_id: int
    status: str
    rating: Optional[int] = None

class UserBookCreate(UserBookBase):
    pass

class UserBook(UserBookBase):
    id: int
    added_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    user_id: int
    book_id: int
    week_number: int

class VoteCreate(VoteBase):
    pass

class Vote(VoteBase):
    id: int
    vote_date: datetime

    class Config:
        from_attributes = True

class ReadingProgressBase(BaseModel):
    user_id: int
    book_id: int
    current_page: int
    total_pages: int
    last_read_at: datetime

class ReadingProgressCreate(ReadingProgressBase):
    pass

class ReadingProgress(ReadingProgressBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WeeklyResultBase(BaseModel):
    week_number: int
    book_id: int
    leader_id: int
    votes_count: int

class WeeklyResultCreate(WeeklyResultBase):
    pass

class WeeklyResult(WeeklyResultBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 