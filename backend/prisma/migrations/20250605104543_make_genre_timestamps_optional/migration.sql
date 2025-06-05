/*
  Warnings:

  - You are about to drop the column `registrationDate` on the `User` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Book" ALTER COLUMN "litresId" DROP NOT NULL;

-- AlterTable
ALTER TABLE "Genre" ALTER COLUMN "createdAt" DROP NOT NULL,
ALTER COLUMN "updatedAt" DROP NOT NULL;

-- AlterTable
ALTER TABLE "User" DROP COLUMN "registrationDate",
ADD COLUMN     "about" TEXT,
ADD COLUMN     "avatar" TEXT;
