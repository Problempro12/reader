-- CreateTable
CREATE TABLE "auth_group" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(150) NOT NULL,

    CONSTRAINT "auth_group_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_group_permissions" (
    "id" BIGSERIAL NOT NULL,
    "group_id" INTEGER NOT NULL,
    "permission_id" INTEGER NOT NULL,

    CONSTRAINT "auth_group_permissions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_permission" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "content_type_id" INTEGER NOT NULL,
    "codename" VARCHAR(100) NOT NULL,

    CONSTRAINT "auth_permission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "authtoken_token" (
    "key" VARCHAR(40) NOT NULL,
    "created" TIMESTAMPTZ(6) NOT NULL,
    "user_id" BIGINT NOT NULL,

    CONSTRAINT "authtoken_token_pkey" PRIMARY KEY ("key")
);

-- CreateTable
CREATE TABLE "books_agecategory" (
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(10) NOT NULL,

    CONSTRAINT "books_agecategory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "books_book" (
    "id" BIGSERIAL NOT NULL,
    "title" VARCHAR(200) NOT NULL,
    "author" VARCHAR(200) NOT NULL,
    "cover" VARCHAR(200) NOT NULL,
    "description" TEXT NOT NULL,
    "is_premium" BOOLEAN NOT NULL,
    "rating" DOUBLE PRECISION NOT NULL,
    "litres_rating" JSONB,
    "series" VARCHAR(200) NOT NULL,
    "translator" VARCHAR(200) NOT NULL,
    "technical" JSONB,
    "created_at" TIMESTAMPTZ(6) NOT NULL,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,
    "age_category_id" BIGINT,
    "genre_id" BIGINT,

    CONSTRAINT "books_book_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "books_genre" (
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(100) NOT NULL,

    CONSTRAINT "books_genre_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "django_admin_log" (
    "id" SERIAL NOT NULL,
    "action_time" TIMESTAMPTZ(6) NOT NULL,
    "object_id" TEXT,
    "object_repr" VARCHAR(200) NOT NULL,
    "action_flag" SMALLINT NOT NULL,
    "change_message" TEXT NOT NULL,
    "content_type_id" INTEGER,
    "user_id" BIGINT NOT NULL,

    CONSTRAINT "django_admin_log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "django_content_type" (
    "id" SERIAL NOT NULL,
    "app_label" VARCHAR(100) NOT NULL,
    "model" VARCHAR(100) NOT NULL,

    CONSTRAINT "django_content_type_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "django_migrations" (
    "id" BIGSERIAL NOT NULL,
    "app" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "applied" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "django_migrations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "django_session" (
    "session_key" VARCHAR(40) NOT NULL,
    "session_data" TEXT NOT NULL,
    "expire_date" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "django_session_pkey" PRIMARY KEY ("session_key")
);

-- CreateTable
CREATE TABLE "token_blacklist_blacklistedtoken" (
    "id" BIGSERIAL NOT NULL,
    "blacklisted_at" TIMESTAMPTZ(6) NOT NULL,
    "token_id" BIGINT NOT NULL,

    CONSTRAINT "token_blacklist_blacklistedtoken_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "token_blacklist_outstandingtoken" (
    "id" BIGSERIAL NOT NULL,
    "token" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ(6),
    "expires_at" TIMESTAMPTZ(6) NOT NULL,
    "user_id" BIGINT,
    "jti" VARCHAR(255) NOT NULL,

    CONSTRAINT "token_blacklist_outstandingtoken_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users_user" (
    "id" BIGSERIAL NOT NULL,
    "password" VARCHAR(128) NOT NULL,
    "last_login" TIMESTAMPTZ(6),
    "is_superuser" BOOLEAN NOT NULL,
    "username" VARCHAR(150) NOT NULL,
    "first_name" VARCHAR(150) NOT NULL,
    "last_name" VARCHAR(150) NOT NULL,
    "is_staff" BOOLEAN NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "date_joined" TIMESTAMPTZ(6) NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "is_premium" BOOLEAN NOT NULL,
    "premium_expiration_date" TIMESTAMPTZ(6),
    "hide_ads" BOOLEAN NOT NULL,
    "avatar" VARCHAR(100),
    "about" TEXT,

    CONSTRAINT "users_user_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users_user_groups" (
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "group_id" INTEGER NOT NULL,

    CONSTRAINT "users_user_groups_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users_user_user_permissions" (
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "permission_id" INTEGER NOT NULL,

    CONSTRAINT "users_user_user_permissions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "auth_group_name_key" ON "auth_group"("name");

-- CreateIndex
CREATE INDEX "auth_group_name_a6ea08ec_like" ON "auth_group"("name");

-- CreateIndex
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions"("group_id");

-- CreateIndex
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions"("permission_id");

-- CreateIndex
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions"("group_id", "permission_id");

-- CreateIndex
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission"("content_type_id");

-- CreateIndex
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission"("content_type_id", "codename");

-- CreateIndex
CREATE UNIQUE INDEX "authtoken_token_user_id_key" ON "authtoken_token"("user_id");

-- CreateIndex
CREATE INDEX "authtoken_token_key_10f0b77e_like" ON "authtoken_token"("key");

-- CreateIndex
CREATE UNIQUE INDEX "books_agecategory_name_key" ON "books_agecategory"("name");

-- CreateIndex
CREATE INDEX "books_agecategory_name_c85a5104_like" ON "books_agecategory"("name");

-- CreateIndex
CREATE INDEX "books_book_age_category_id_31222d13" ON "books_book"("age_category_id");

-- CreateIndex
CREATE INDEX "books_book_genre_id_f94e1a9b" ON "books_book"("genre_id");

-- CreateIndex
CREATE UNIQUE INDEX "books_genre_name_key" ON "books_genre"("name");

-- CreateIndex
CREATE INDEX "books_genre_name_b6ee53e9_like" ON "books_genre"("name");

-- CreateIndex
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log"("content_type_id");

-- CreateIndex
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type"("app_label", "model");

-- CreateIndex
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session"("expire_date");

-- CreateIndex
CREATE INDEX "django_session_session_key_c0390e0f_like" ON "django_session"("session_key");

-- CreateIndex
CREATE UNIQUE INDEX "token_blacklist_blacklistedtoken_token_id_key" ON "token_blacklist_blacklistedtoken"("token_id");

-- CreateIndex
CREATE UNIQUE INDEX "token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq" ON "token_blacklist_outstandingtoken"("jti");

-- CreateIndex
CREATE INDEX "token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_like" ON "token_blacklist_outstandingtoken"("jti");

-- CreateIndex
CREATE INDEX "token_blacklist_outstandingtoken_user_id_83bc629a" ON "token_blacklist_outstandingtoken"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_user_username_key" ON "users_user"("username");

-- CreateIndex
CREATE UNIQUE INDEX "users_user_email_key" ON "users_user"("email");

-- CreateIndex
CREATE INDEX "users_user_email_243f6e77_like" ON "users_user"("email");

-- CreateIndex
CREATE INDEX "users_user_username_06e46fe6_like" ON "users_user"("username");

-- CreateIndex
CREATE INDEX "users_user_groups_group_id_9afc8d0e" ON "users_user_groups"("group_id");

-- CreateIndex
CREATE INDEX "users_user_groups_user_id_5f6f5a90" ON "users_user_groups"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_user_groups_user_id_group_id_b88eab82_uniq" ON "users_user_groups"("user_id", "group_id");

-- CreateIndex
CREATE INDEX "users_user_user_permissions_permission_id_0b93982e" ON "users_user_user_permissions"("permission_id");

-- CreateIndex
CREATE INDEX "users_user_user_permissions_user_id_20aca447" ON "users_user_user_permissions"("user_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_user_user_permissions_user_id_permission_id_43338c45_uniq" ON "users_user_user_permissions"("user_id", "permission_id");

-- AddForeignKey
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_2f476e4b_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "authtoken_token" ADD CONSTRAINT "authtoken_token_user_id_35299eff_fk_users_user_id" FOREIGN KEY ("user_id") REFERENCES "users_user"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "books_book" ADD CONSTRAINT "books_book_age_category_id_31222d13_fk_books_agecategory_id" FOREIGN KEY ("age_category_id") REFERENCES "books_agecategory"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "books_book" ADD CONSTRAINT "books_book_genre_id_f94e1a9b_fk_books_genre_id" FOREIGN KEY ("genre_id") REFERENCES "books_genre"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "django_admin_log" ADD CONSTRAINT "django_admin_log_content_type_id_c4bce8eb_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "django_admin_log" ADD CONSTRAINT "django_admin_log_user_id_c564eba6_fk_users_user_id" FOREIGN KEY ("user_id") REFERENCES "users_user"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "token_blacklist_blacklistedtoken" ADD CONSTRAINT "token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk" FOREIGN KEY ("token_id") REFERENCES "token_blacklist_outstandingtoken"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "token_blacklist_outstandingtoken" ADD CONSTRAINT "token_blacklist_outs_user_id_83bc629a_fk_users_use" FOREIGN KEY ("user_id") REFERENCES "users_user"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "users_user_groups" ADD CONSTRAINT "users_user_groups_group_id_9afc8d0e_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "users_user_groups" ADD CONSTRAINT "users_user_groups_user_id_5f6f5a90_fk_users_user_id" FOREIGN KEY ("user_id") REFERENCES "users_user"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "users_user_user_permissions" ADD CONSTRAINT "users_user_user_perm_permission_id_0b93982e_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- AddForeignKey
ALTER TABLE "users_user_user_permissions" ADD CONSTRAINT "users_user_user_permissions_user_id_20aca447_fk_users_user_id" FOREIGN KEY ("user_id") REFERENCES "users_user"("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
