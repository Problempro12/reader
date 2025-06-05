/*
  Warnings:

  - The `genreId` column on the `Book` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - The primary key for the `Genre` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - The `id` column on the `Genre` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - The `parentId` column on the `Genre` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - The `genreId` column on the `WeeklyResult` table would be dropped and recreated. This will lead to data loss if there is data in the column.

*/
-- DropForeignKey
ALTER TABLE "Book" DROP CONSTRAINT "Book_genreId_fkey";

-- DropForeignKey
ALTER TABLE "Genre" DROP CONSTRAINT "Genre_parentId_fkey";

-- DropForeignKey
ALTER TABLE "WeeklyResult" DROP CONSTRAINT "WeeklyResult_genreId_fkey";

-- AlterTable
ALTER TABLE "Book" DROP COLUMN "genreId",
ADD COLUMN     "genreId" INTEGER;

-- AlterTable
ALTER TABLE "Genre" DROP CONSTRAINT "Genre_pkey",
DROP COLUMN "id",
ADD COLUMN     "id" SERIAL NOT NULL,
DROP COLUMN "parentId",
ADD COLUMN     "parentId" INTEGER,
ADD CONSTRAINT "Genre_pkey" PRIMARY KEY ("id");

-- AlterTable
ALTER TABLE "WeeklyResult" DROP COLUMN "genreId",
ADD COLUMN     "genreId" INTEGER;

-- CreateIndex
CREATE UNIQUE INDEX "WeeklyResult_weekNumber_genreId_ageCategoryId_key" ON "WeeklyResult"("weekNumber", "genreId", "ageCategoryId");

-- AddForeignKey
ALTER TABLE "Genre" ADD CONSTRAINT "Genre_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WeeklyResult" ADD CONSTRAINT "WeeklyResult_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE SET NULL ON UPDATE CASCADE;
