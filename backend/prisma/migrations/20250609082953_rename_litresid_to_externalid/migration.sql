/*
  Warnings:

  - You are about to drop the column `litresId` on the `Book` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[externalId]` on the table `Book` will be added. If there are existing duplicate values, this will fail.

*/
-- DropIndex
DROP INDEX "Book_litresId_key";

-- AlterTable
ALTER TABLE "Book" DROP COLUMN "litresId",
ADD COLUMN     "externalId" TEXT;

-- CreateIndex
CREATE UNIQUE INDEX "Book_externalId_key" ON "Book"("externalId");
