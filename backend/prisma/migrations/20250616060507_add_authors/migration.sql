/*
  Warnings:

  - You are about to drop the column `author` on the `Book` table. All the data in the column will be lost.
  - You are about to drop the `books_agecategory` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `books_book` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `books_genre` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `authorId` to the `Book` table without a default value. This is not possible if the table is not empty.
  - Made the column `genreId` on table `Book` required. This step will fail if there are existing NULL values in that column.

*/
-- DropForeignKey
ALTER TABLE "Book" DROP CONSTRAINT "Book_genreId_fkey";

-- DropForeignKey
ALTER TABLE "books_book" DROP CONSTRAINT "books_book_age_category_id_31222d13_fk_books_agecategory_id";

-- DropForeignKey
ALTER TABLE "books_book" DROP CONSTRAINT "books_book_genre_id_f94e1a9b_fk_books_genre_id";

-- AlterTable
ALTER TABLE "Book" DROP COLUMN "author",
ADD COLUMN     "authorId" INTEGER NOT NULL,
ALTER COLUMN "genreId" SET NOT NULL;

-- DropTable
DROP TABLE "books_agecategory";

-- DropTable
DROP TABLE "books_book";

-- DropTable
DROP TABLE "books_genre";

-- CreateTable
CREATE TABLE "Author" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Author_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Author_name_key" ON "Author"("name");

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES "Author"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
