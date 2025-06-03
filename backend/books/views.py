from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from prisma import Prisma
from .serializers import BookSerializer, GenreSerializer, AgeCategorySerializer
from datetime import datetime
import asyncio

def run_async(coro):
    return asyncio.run(coro)

# Create your views here.

class BookListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_queryset(self):
        async def get_books():
            prisma = Prisma()
            await prisma.connect()
            books = await prisma.book.find_many()
            await prisma.disconnect()
            return books
        return run_async(get_books())

    def perform_create(self, serializer):
        async def create_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.create(data=serializer.validated_data)
            await prisma.disconnect()
            return book
        return run_async(create_book())

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_object(self):
        async def get_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.find_unique(where={'id': self.kwargs['pk']})
            await prisma.disconnect()
            return book
        return run_async(get_book())

    def perform_update(self, serializer):
        async def update_book():
            prisma = Prisma()
            await prisma.connect()
            book = await prisma.book.update(
                where={'id': self.kwargs['pk']},
                data=serializer.validated_data
            )
            await prisma.disconnect()
            return book
        return run_async(update_book())

    def perform_destroy(self, instance):
        async def delete_book():
            prisma = Prisma()
            await prisma.connect()
            await prisma.book.delete(where={'id': self.kwargs['pk']})
            await prisma.disconnect()
        run_async(delete_book())

class GenreListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenreSerializer

    def get_queryset(self):
        async def get_genres():
            prisma = Prisma()
            await prisma.connect()
            genres = await prisma.genre.find_many()
            await prisma.disconnect()
            return genres
        return run_async(get_genres())

class AgeCategoryListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgeCategorySerializer

    def get_queryset(self):
        async def get_categories():
            prisma = Prisma()
            await prisma.connect()
            categories = await prisma.agecategory.find_many()
            await prisma.disconnect()
            return categories
        return run_async(get_categories())

class VoteCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        async def create_vote():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            vote = await prisma.vote.create(
                data={
                    'userId': self.request.user.id,
                    'bookId': serializer.validated_data['bookId'],
                    'weekNumber': current_week,
                }
            )
            await prisma.disconnect()
            return vote
        return run_async(create_vote())

class ProgressCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        async def create_progress():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            progress = await prisma.readingprogress.create(
                data={
                    'userId': self.request.user.id,
                    'bookId': serializer.validated_data['bookId'],
                    'weekNumber': current_week,
                    'marks': serializer.validated_data.get('marks', 1),
                }
            )
            await prisma.disconnect()
            return progress
        return run_async(create_progress())

class WeeklyResultListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        async def get_results():
            prisma = Prisma()
            await prisma.connect()
            current_week = datetime.now().isocalendar()[1]
            results = await prisma.weeklyresult.find_many(
                where={'weekNumber': current_week},
                include={
                    'genre': True,
                    'ageCategory': True,
                    'book': True,
                    'leader': True,
                }
            )
            await prisma.disconnect()
            return results
        return run_async(get_results())
