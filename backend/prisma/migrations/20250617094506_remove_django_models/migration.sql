/*
  Warnings:

  - You are about to drop the column `criteria` on the `Achievement` table. All the data in the column will be lost.
  - You are about to drop the column `reward` on the `Achievement` table. All the data in the column will be lost.
  - You are about to drop the column `type` on the `Achievement` table. All the data in the column will be lost.
  - You are about to drop the column `author` on the `Book` table. All the data in the column will be lost.
  - You are about to drop the column `achievedAt` on the `UserAchievement` table. All the data in the column will be lost.
  - You are about to drop the `auth_group` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `auth_group_permissions` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `auth_permission` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `authtoken_token` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `books_agecategory` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `books_book` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `books_genre` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `django_admin_log` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `django_content_type` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `django_migrations` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `django_session` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `token_blacklist_blacklistedtoken` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `token_blacklist_outstandingtoken` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `users_user` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `users_user_groups` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `users_user_user_permissions` table. If the table is not empty, all the data it contains will be lost.
  - A unique constraint covering the columns `[username]` on the table `User` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `authorId` to the `Book` table without a default value. This is not possible if the table is not empty.
  - Made the column `genreId` on table `Book` required. This step will fail if there are existing NULL values in that column.

*/
-- DropForeignKey
ALTER TABLE "Book" DROP CONSTRAINT "Book_genreId_fkey";

-- DropForeignKey
ALTER TABLE "auth_group_permissions" DROP CONSTRAINT "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm";

-- DropForeignKey
ALTER TABLE "auth_group_permissions" DROP CONSTRAINT "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id";

-- DropForeignKey
ALTER TABLE "auth_permission" DROP CONSTRAINT "auth_permission_content_type_id_2f476e4b_fk_django_co";

-- DropForeignKey
ALTER TABLE "authtoken_token" DROP CONSTRAINT "authtoken_token_user_id_35299eff_fk_users_user_id";

-- DropForeignKey
ALTER TABLE "books_book" DROP CONSTRAINT "books_book_age_category_id_31222d13_fk_books_agecategory_id";

-- DropForeignKey
ALTER TABLE "books_book" DROP CONSTRAINT "books_book_genre_id_f94e1a9b_fk_books_genre_id";

-- DropForeignKey
ALTER TABLE "django_admin_log" DROP CONSTRAINT "django_admin_log_content_type_id_c4bce8eb_fk_django_co";

-- DropForeignKey
ALTER TABLE "django_admin_log" DROP CONSTRAINT "django_admin_log_user_id_c564eba6_fk_users_user_id";

-- DropForeignKey
ALTER TABLE "token_blacklist_blacklistedtoken" DROP CONSTRAINT "token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk";

-- DropForeignKey
ALTER TABLE "token_blacklist_outstandingtoken" DROP CONSTRAINT "token_blacklist_outs_user_id_83bc629a_fk_users_use";

-- DropForeignKey
ALTER TABLE "users_user_groups" DROP CONSTRAINT "users_user_groups_group_id_9afc8d0e_fk_auth_group_id";

-- DropForeignKey
ALTER TABLE "users_user_groups" DROP CONSTRAINT "users_user_groups_user_id_5f6f5a90_fk_users_user_id";

-- DropForeignKey
ALTER TABLE "users_user_user_permissions" DROP CONSTRAINT "users_user_user_perm_permission_id_0b93982e_fk_auth_perm";

-- DropForeignKey
ALTER TABLE "users_user_user_permissions" DROP CONSTRAINT "users_user_user_permissions_user_id_20aca447_fk_users_user_id";

-- AlterTable
ALTER TABLE "Achievement" DROP COLUMN "criteria",
DROP COLUMN "reward",
DROP COLUMN "type";

-- AlterTable
ALTER TABLE "Book" DROP COLUMN "author",
ADD COLUMN     "authorId" INTEGER NOT NULL,
ALTER COLUMN "genreId" SET NOT NULL;

-- AlterTable
ALTER TABLE "User" ADD COLUMN     "isActive" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "isStaff" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "isSuperuser" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "lastLogin" TIMESTAMP(3);

-- AlterTable
ALTER TABLE "UserAchievement" DROP COLUMN "achievedAt",
ADD COLUMN     "earnedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- DropTable
DROP TABLE "auth_group";

-- DropTable
DROP TABLE "auth_group_permissions";

-- DropTable
DROP TABLE "auth_permission";

-- DropTable
DROP TABLE "authtoken_token";

-- DropTable
DROP TABLE "books_agecategory";

-- DropTable
DROP TABLE "books_book";

-- DropTable
DROP TABLE "books_genre";

-- DropTable
DROP TABLE "django_admin_log";

-- DropTable
DROP TABLE "django_content_type";

-- DropTable
DROP TABLE "django_migrations";

-- DropTable
DROP TABLE "django_session";

-- DropTable
DROP TABLE "token_blacklist_blacklistedtoken";

-- DropTable
DROP TABLE "token_blacklist_outstandingtoken";

-- DropTable
DROP TABLE "users_user";

-- DropTable
DROP TABLE "users_user_groups";

-- DropTable
DROP TABLE "users_user_user_permissions";

-- CreateTable
CREATE TABLE "Group" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Permission" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "codename" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Permission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserGroup" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "groupId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "UserGroup_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "UserPermission" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "permissionId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "UserPermission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GroupPermission" (
    "id" SERIAL NOT NULL,
    "groupId" INTEGER NOT NULL,
    "permissionId" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "GroupPermission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Token" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "token" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Token_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Session" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "sessionKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Author" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Author_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Group_name_key" ON "Group"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Permission_name_key" ON "Permission"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Permission_codename_key" ON "Permission"("codename");

-- CreateIndex
CREATE UNIQUE INDEX "UserGroup_userId_groupId_key" ON "UserGroup"("userId", "groupId");

-- CreateIndex
CREATE UNIQUE INDEX "UserPermission_userId_permissionId_key" ON "UserPermission"("userId", "permissionId");

-- CreateIndex
CREATE UNIQUE INDEX "GroupPermission_groupId_permissionId_key" ON "GroupPermission"("groupId", "permissionId");

-- CreateIndex
CREATE UNIQUE INDEX "Token_token_key" ON "Token"("token");

-- CreateIndex
CREATE UNIQUE INDEX "Session_sessionKey_key" ON "Session"("sessionKey");

-- CreateIndex
CREATE UNIQUE INDEX "Author_name_key" ON "Author"("name");

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");

-- AddForeignKey
ALTER TABLE "UserGroup" ADD CONSTRAINT "UserGroup_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserGroup" ADD CONSTRAINT "UserGroup_groupId_fkey" FOREIGN KEY ("groupId") REFERENCES "Group"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserPermission" ADD CONSTRAINT "UserPermission_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "UserPermission" ADD CONSTRAINT "UserPermission_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES "Permission"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GroupPermission" ADD CONSTRAINT "GroupPermission_groupId_fkey" FOREIGN KEY ("groupId") REFERENCES "Group"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GroupPermission" ADD CONSTRAINT "GroupPermission_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES "Permission"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Token" ADD CONSTRAINT "Token_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Session" ADD CONSTRAINT "Session_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES "Author"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Book" ADD CONSTRAINT "Book_genreId_fkey" FOREIGN KEY ("genreId") REFERENCES "Genre"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
