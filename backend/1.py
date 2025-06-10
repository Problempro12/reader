from prisma import Prisma
import asyncio

async def create_genre():
    prisma = Prisma()
    await prisma.connect()
    genre = await prisma.genre.create(data={'name': 'Science Fiction'})
    print("Создан жанр:", genre)
    await prisma.disconnect()

asyncio.run(create_genre())