/*
  Warnings:

  - The primary key for the `Genre` table will be changed. If it partially fails, the table could be left without primary key constraint.

*/
-- DropForeignKey
ALTER TABLE "Book" DROP CONSTRAINT "Book_genreId_fkey";

-- DropForeignKey
ALTER TABLE "Genre" DROP CONSTRAINT "Genre_parentId_fkey";

-- DropForeignKey
ALTER TABLE "WeeklyResult" DROP CONSTRAINT "WeeklyResult_genreId_fkey";

-- DropIndex
DROP INDEX "Genre_name_key";

-- AlterTable
ALTER TABLE "Book" ALTER COLUMN "genreId" DROP NOT NULL,
ALTER COLUMN "genreId" SET DATA TYPE TEXT;

-- AlterTable
ALTER TABLE "Genre" DROP CONSTRAINT "Genre_pkey",
ALTER COLUMN "id" DROP DEFAULT,
ALTER COLUMN "id" SET DATA TYPE TEXT,
ALTER COLUMN "parentId" SET DATA TYPE TEXT,
ALTER COLUMN "updatedAt" DROP DEFAULT,
ADD CONSTRAINT "Genre_pkey" PRIMARY KEY ("id");
DROP SEQUENCE "Genre_id_seq";

-- AlterTable
ALTER TABLE "WeeklyResult" ALTER COLUMN "genreId" DROP NOT NULL,
ALTER COLUMN "genreId" SET DATA TYPE TEXT;

-- AddForeignKey
ALTER TABLE "Genre" ADD CONSTRAINT "Genre_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WeeklyResult" ADD CONSTRAINT "WeeklyResult_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;
