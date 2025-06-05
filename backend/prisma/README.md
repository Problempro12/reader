# Документация схемы базы данных

## Обзор

База данных использует Prisma ORM и PostgreSQL. Схема определяет все модели данных и их взаимосвязи.

## Модели

### User
```prisma
model User {
  id            String           @id @default(uuid())
  email         String           @unique
  username      String           @unique
  is_premium    Boolean          @default(false)
  is_staff      Boolean          @default(false)
  is_superuser  Boolean          @default(false)
  votes         Vote[]
  progress      ReadingProgress[]
  books         UserBook[]
  notifications Notification[]
  createdAt     DateTime         @default(now())
  updatedAt     DateTime         @updatedAt
}
```

### Book
```prisma
model Book {
  id            String           @id @default(uuid())
  title         String
  author        String
  genre         Genre            @relation(fields: [genreId], references: [id])
  genreId       String
  ageCategory   AgeCategory      @relation(fields: [ageCategoryId], references: [id])
  ageCategoryId String
  votes         Vote[]
  progress      ReadingProgress[]
  users         UserBook[]
  createdAt     DateTime         @default(now())
  updatedAt     DateTime         @updatedAt
}
```

### Genre
```prisma
model Genre {
  id        String   @id @default(uuid())
  name      String   @unique
  books     Book[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

### AgeCategory
```prisma
model AgeCategory {
  id        String   @id @default(uuid())
  name      String   @unique
  books     Book[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

### Vote
```prisma
model Vote {
  id         String   @id @default(uuid())
  user       User     @relation(fields: [userId], references: [id])
  userId     String
  book       Book     @relation(fields: [bookId], references: [id])
  bookId     String
  weekNumber Int
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  @@unique([userId, bookId, weekNumber])
}
```

### ReadingProgress
```prisma
model ReadingProgress {
  id         String   @id @default(uuid())
  user       User     @relation(fields: [userId], references: [id])
  userId     String
  book       Book     @relation(fields: [bookId], references: [id])
  bookId     String
  weekNumber Int
  marks      Int      @default(1)
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  @@unique([userId, bookId, weekNumber])
}
```

### UserBook
```prisma
model UserBook {
  id        String   @id @default(uuid())
  user      User     @relation(fields: [userId], references: [id])
  userId    String
  book      Book     @relation(fields: [bookId], references: [id])
  bookId    String
  status    String   // reading, completed, planned
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([userId, bookId])
}
```

### Notification
```prisma
model Notification {
  id        String   @id @default(uuid())
  user      User     @relation(fields: [userId], references: [id])
  userId    String
  message   String
  isRead    Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

## Индексы

База данных использует следующие индексы для оптимизации запросов:

1. Уникальные индексы:
   - User: email, username
   - Genre: name
   - AgeCategory: name
   - Vote: [userId, bookId, weekNumber]
   - ReadingProgress: [userId, bookId, weekNumber]
   - UserBook: [userId, bookId]

2. Внешние ключи:
   - Book -> Genre
   - Book -> AgeCategory
   - Vote -> User
   - Vote -> Book
   - ReadingProgress -> User
   - ReadingProgress -> Book
   - UserBook -> User
   - UserBook -> Book
   - Notification -> User

## Миграции

Для применения изменений в схеме базы данных используйте следующие команды:

```bash
# Создание миграции
npx prisma migrate dev --name <название_миграции>

# Применение миграций
npx prisma migrate deploy

# Сброс базы данных (только для разработки)
npx prisma migrate reset
```

## Запросы

### Примеры часто используемых запросов

1. Получение всех книг с жанром и возрастной категорией:
```prisma
const books = await prisma.book.findMany({
  include: {
    genre: true,
    ageCategory: true
  }
});
```

2. Получение прогресса чтения пользователя:
```prisma
const progress = await prisma.readingProgress.findMany({
  where: {
    userId: userId,
    weekNumber: currentWeek
  },
  include: {
    book: true
  }
});
```

3. Получение статистики голосов за неделю:
```prisma
const votes = await prisma.vote.groupBy({
  by: ['bookId'],
  where: {
    weekNumber: currentWeek
  },
  _count: {
    bookId: true
  }
});
```

## Рекомендации по использованию

1. Всегда используйте транзакции при выполнении связанных операций
2. Используйте include для получения связанных данных
3. Применяйте пагинацию для больших наборов данных
4. Используйте select для оптимизации запросов
5. Регулярно делайте резервные копии базы данных 