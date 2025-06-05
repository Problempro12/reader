from prisma import Prisma
import asyncio

async def clear_genres():
    prisma = Prisma()
    await prisma.connect()
    await prisma.genre.delete_many()
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_genres()) 