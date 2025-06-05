from prisma import Prisma
import asyncio

async def clear_all_genre_related():
    prisma = Prisma()
    await prisma.connect()
    await prisma.book.delete_many()
    await prisma.weeklyresult.delete_many()
    await prisma.genre.delete_many()
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_all_genre_related()) 