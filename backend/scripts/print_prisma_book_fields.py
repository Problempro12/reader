from prisma import Prisma
import asyncio

async def main():
    prisma = Prisma()
    await prisma.connect()
    books = await prisma.book.find_many()
    if books:
        print(books[0])
        print('FIELDS:', list(books[0].keys()))
    else:
        print('NO BOOKS')
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main()) 