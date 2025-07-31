from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from prisma.models import Book, Author, Genre, AgeCategory
from prisma import Prisma

router = APIRouter()

@router.get("/books")
async def get_books(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    age_category: Optional[str] = None,
    rating: Optional[float] = None,
    sort_by: Optional[str] = None
):
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Базовый запрос
        query = {
            "skip": (page - 1) * per_page,
            "take": per_page,
            "include": {
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        }
        
        # Добавляем фильтры
        where = {}
        if search:
            where["OR"] = [
                {"title": {"contains": search}},
                {"author": {"name": {"contains": search}}}
            ]
        if genre:
            where["genre"] = {"name": genre}
        if age_category:
            where["ageCategory"] = {"name": age_category}
        if rating:
            where["rating"] = {"gte": rating}
        
        if where:
            query["where"] = where
        
        # Добавляем сортировку
        if sort_by:
            if sort_by == "rating":
                query["order"] = {"rating": "desc"}
            elif sort_by == "newest":
                query["order"] = {"createdAt": "desc"}
            elif sort_by == "alphabet":
                query["order"] = {"title": "asc"}
        
        # Получаем книги
        books = await prisma.book.find_many(**query)
        total = await prisma.book.count(where=where if where else None)
        
        return {
            "books": books,
            "total": total,
            "page": page,
            "perPage": per_page
        }
    finally:
        await prisma.disconnect()

@router.get("/books/top")
async def get_top_books():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        books = await prisma.book.find_many(
            take=5,
            order={"rating": "desc"},
            include={
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        )
        return books
    finally:
        await prisma.disconnect()

@router.get("/books/recommended")
async def get_recommended_books():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Здесь можно добавить более сложную логику рекомендаций
        books = await prisma.book.find_many(
            take=5,
            order={"rating": "desc"},
            include={
                "author": True,
                "genre": True,
                "ageCategory": True
            }
        )
        return books
    finally:
        await prisma.disconnect()

@router.post("/books/{book_id}/rate")
async def rate_book(book_id: int, rating: float):
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        book = await prisma.book.find_unique(where={"id": book_id})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Обновляем рейтинг
        updated_book = await prisma.book.update(
            where={"id": book_id},
            data={
                "rating": rating,
                "rating_count": {"increment": 1}
            }
        )
        return updated_book
    finally:
        await prisma.disconnect() 