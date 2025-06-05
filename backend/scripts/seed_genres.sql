-- Сначала очищаем таблицу жанров
TRUNCATE TABLE "Genre" CASCADE;

-- Добавляем основные жанры
INSERT INTO "Genre" ("name", "createdAt", "updatedAt") VALUES
('Детективы', NOW(), NOW()),
('Фантастика', NOW(), NOW()),
('Фэнтези', NOW(), NOW()),
('Любовные романы', NOW(), NOW()),
('Эротика и секс', NOW(), NOW()),
('Ужасы / мистика', NOW(), NOW()),
('Боевики, остросюжетная литература', NOW(), NOW()),
('Юмористическая литература', NOW(), NOW()),
('Приключения', NOW(), NOW()),
('Классика жанра', NOW(), NOW()),
('Современная проза', NOW(), NOW()),
('Классическая литература', NOW(), NOW()),
('Биографии и мемуары', NOW(), NOW()),
('Об истории серьезно', NOW(), NOW()),
('Стихи, поэзия', NOW(), NOW()),
('Пьесы, драматургия', NOW(), NOW());

-- Добавляем поджанры для Детективов
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Классический детектив'),
    ('Полицейский детектив'),
    ('Криминальный детектив'),
    ('Шпионский детектив'),
    ('Исторический детектив'),
    ('Психологический детектив'),
    ('Иронический детектив'),
    ('Политический детектив'),
    ('Технотриллер')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Детективы';

-- Добавляем поджанры для Фантастики
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Научная фантастика'),
    ('Космическая фантастика'),
    ('Альтернативная история'),
    ('Антиутопия'),
    ('Киберпанк'),
    ('Постапокалипсис'),
    ('Социальная фантастика'),
    ('Технофэнтези'),
    ('Утопия'),
    ('Фантастический боевик'),
    ('Фантастическая проза'),
    ('Фантастические рассказы')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Фантастика';

-- Добавляем поджанры для Фэнтези
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Героическое фэнтези'),
    ('Городское фэнтези'),
    ('Детское фэнтези'),
    ('Историческое фэнтези'),
    ('Классическое фэнтези'),
    ('Любовное фэнтези'),
    ('Мистическое фэнтези'),
    ('Попаданцы'),
    ('Романтическое фэнтези'),
    ('Славянское фэнтези'),
    ('Темное фэнтези'),
    ('Эпическое фэнтези'),
    ('Юмористическое фэнтези'),
    ('Фэнтези про драконов')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Фэнтези';

-- Добавляем поджанры для Любовных романов
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Исторические любовные романы'),
    ('Короткие любовные романы'),
    ('Любовно-фантастические романы'),
    ('Любовно-приключенческие романы'),
    ('Остросюжетные любовные романы'),
    ('Романтическая проза'),
    ('Современные любовные романы')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Любовные романы';

-- Добавляем поджанры для Эротики и секса
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Эротическая литература'),
    ('Секс-руководства'),
    ('Эротические романы'),
    ('Эротические рассказы'),
    ('Эротическое фэнтези')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Эротика и секс';

-- Добавляем поджанры для Ужасов / мистики
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Мистика'),
    ('Ужасы')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Ужасы / мистика';

-- Добавляем поджанры для Боевиков
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Боевики'),
    ('Криминальный боевик'),
    ('Политический боевик'),
    ('Шпионский боевик'),
    ('Экшн')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Боевики, остросюжетная литература';

-- Добавляем поджанры для Юмористической литературы
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Анекдоты'),
    ('Сатира'),
    ('Юмористическая проза'),
    ('Юмористические рассказы')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Юмористическая литература';

-- Добавляем поджанры для Приключений
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Вестерн'),
    ('Исторические приключения'),
    ('Морские приключения'),
    ('Приключения в современном мире'),
    ('Приключения про индейцев'),
    ('Путешествия и география'),
    ('Экстремальные виды спорта')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Приключения';

-- Добавляем поджанры для Классики жанра
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Зарубежная классика'),
    ('Классическая проза'),
    ('Литература 18 века'),
    ('Литература 19 века'),
    ('Литература 20 века')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Классика жанра';

-- Добавляем поджанры для Современной прозы
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Современная зарубежная литература'),
    ('Современная русская литература'),
    ('Современные любовные романы'),
    ('Современные детективы'),
    ('Современная проза')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Современная проза';

-- Добавляем поджанры для Классической литературы
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Античная литература'),
    ('Древневосточная литература'),
    ('Древнерусская литература'),
    ('Литература Средних веков'),
    ('Литература эпохи Возрождения'),
    ('Русская классика'),
    ('Современная классика'),
    ('Средневековая литература'),
    ('Старинная литература'),
    ('Эпос и фольклор')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Классическая литература';

-- Добавляем поджанры для Биографий и мемуаров
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Биографии'),
    ('Мемуары'),
    ('Публицистика')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Биографии и мемуары';

-- Добавляем поджанры для Об истории серьезно
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Археология'),
    ('Исторические исследования'),
    ('Исторические личности'),
    ('История')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Об истории серьезно';

-- Добавляем поджанры для Стихов, поэзии
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Зарубежная поэзия'),
    ('Русская поэзия'),
    ('Современная поэзия')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Стихи, поэзия';

-- Добавляем поджанры для Пьес, драматургии
INSERT INTO "Genre" ("name", "parentId", "createdAt", "updatedAt")
SELECT subgenre, g.id, NOW(), NOW()
FROM (VALUES 
    ('Зарубежная драматургия'),
    ('Русская драматургия'),
    ('Современная драматургия')
) AS subgenres(subgenre)
CROSS JOIN "Genre" g
WHERE g.name = 'Пьесы, драматургия'; 