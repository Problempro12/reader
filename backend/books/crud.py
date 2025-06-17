from typing import List, Optional, Dict, Any
from datetime import datetime
from prisma import Prisma
from .schemas import (
    BookCreate, Book, AuthorCreate, Author,
    GenreCreate, Genre, AgeCategoryCreate, AgeCategory,
    UserBookCreate, UserBook, VoteCreate, Vote,
    ReadingProgressCreate, ReadingProgress,
    WeeklyResultCreate, WeeklyResult
)

class BookCRUD:
    def __init__(self):
        self.prisma = Prisma()

    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        await self.prisma.disconnect()

    # Book operations
    async def create_book(self, book: BookCreate) -> Book:
        return await self.prisma.book.create(data=book.dict())

    async def get_book(self, book_id: int) -> Optional[Book]:
        return await self.prisma.book.find_unique(where={'id': book_id})

    async def get_books(
        self,
        skip: int = 0,
        limit: int = 10,
        genre_id: Optional[int] = None,
        age_category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        is_premium: Optional[bool] = None
    ) -> List[Book]:
        where = {}
        if genre_id:
            where['genre_id'] = genre_id
        if age_category_id:
            where['age_category_id'] = age_category_id
        if author_id:
            where['author_id'] = author_id
        if is_premium is not None:
            where['is_premium'] = is_premium

        return await self.prisma.book.find_many(
            where=where,
            skip=skip,
            take=limit,
            order_by={'created_at': 'desc'}
        )

    async def update_book(self, book_id: int, book_data: Dict[str, Any]) -> Optional[Book]:
        return await self.prisma.book.update(
            where={'id': book_id},
            data=book_data
        )

    async def delete_book(self, book_id: int) -> Optional[Book]:
        return await self.prisma.book.delete(where={'id': book_id})

    # Author operations
    async def create_author(self, author: AuthorCreate) -> Author:
        return await self.prisma.author.create(data=author.dict())

    async def get_author(self, author_id: int) -> Optional[Author]:
        return await self.prisma.author.find_unique(where={'id': author_id})

    async def get_authors(self, skip: int = 0, limit: int = 10) -> List[Author]:
        return await self.prisma.author.find_many(
            skip=skip,
            take=limit,
            order_by={'name': 'asc'}
        )

    # Genre operations
    async def create_genre(self, genre: GenreCreate) -> Genre:
        return await self.prisma.genre.create(data=genre.dict())

    async def get_genre(self, genre_id: int) -> Optional[Genre]:
        return await self.prisma.genre.find_unique(where={'id': genre_id})

    async def get_genres(self, skip: int = 0, limit: int = 10) -> List[Genre]:
        return await self.prisma.genre.find_many(
            skip=skip,
            take=limit,
            order_by={'name': 'asc'}
        )

    # Age Category operations
    async def create_age_category(self, age_category: AgeCategoryCreate) -> AgeCategory:
        return await self.prisma.agecategory.create(data=age_category.dict())

    async def get_age_category(self, age_category_id: int) -> Optional[AgeCategory]:
        return await self.prisma.agecategory.find_unique(where={'id': age_category_id})

    async def get_age_categories(self, skip: int = 0, limit: int = 10) -> List[AgeCategory]:
        return await self.prisma.agecategory.find_many(
            skip=skip,
            take=limit,
            order_by={'name': 'asc'}
        )

    # User Book operations
    async def create_user_book(self, user_book: UserBookCreate) -> UserBook:
        return await self.prisma.userbook.create(data=user_book.dict())

    async def get_user_book(self, user_id: int, book_id: int) -> Optional[UserBook]:
        return await self.prisma.userbook.find_unique(
            where={
                'user_id_book_id': {
                    'user_id': user_id,
                    'book_id': book_id
                }
            }
        )

    async def get_user_books(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[UserBook]:
        where = {'user_id': user_id}
        if status:
            where['status'] = status

        return await self.prisma.userbook.find_many(
            where=where,
            skip=skip,
            take=limit,
            order_by={'added_at': 'desc'}
        )

    # Vote operations
    async def create_vote(self, vote: VoteCreate) -> Vote:
        return await self.prisma.vote.create(data=vote.dict())

    async def get_user_votes(
        self,
        user_id: int,
        week_number: Optional[int] = None
    ) -> List[Vote]:
        where = {'user_id': user_id}
        if week_number is not None:
            where['week_number'] = week_number

        return await self.prisma.vote.find_many(where=where)

    # Reading Progress operations
    async def create_reading_progress(self, progress: ReadingProgressCreate) -> ReadingProgress:
        return await self.prisma.readingprogress.create(data=progress.dict())

    async def get_reading_progress(
        self,
        user_id: int,
        book_id: int
    ) -> Optional[ReadingProgress]:
        return await self.prisma.readingprogress.find_unique(
            where={
                'user_id_book_id': {
                    'user_id': user_id,
                    'book_id': book_id
                }
            }
        )

    async def update_reading_progress(
        self,
        user_id: int,
        book_id: int,
        current_page: int,
        total_pages: int
    ) -> Optional[ReadingProgress]:
        return await self.prisma.readingprogress.update(
            where={
                'user_id_book_id': {
                    'user_id': user_id,
                    'book_id': book_id
                }
            },
            data={
                'current_page': current_page,
                'total_pages': total_pages,
                'last_read_at': datetime.now()
            }
        )

    # Weekly Result operations
    async def create_weekly_result(self, result: WeeklyResultCreate) -> WeeklyResult:
        return await self.prisma.weeklyresult.create(data=result.dict())

    async def get_weekly_results(
        self,
        week_number: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[WeeklyResult]:
        where = {}
        if week_number is not None:
            where['week_number'] = week_number

        return await self.prisma.weeklyresult.find_many(
            where=where,
            skip=skip,
            take=limit,
            order_by={'votes_count': 'desc'}
        ) 