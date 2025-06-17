CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_EXPOSE_HEADERS = [
    'content-length',
    'content-type',
]

# Разрешаем все заголовки
CORS_ALLOW_ALL_HEADERS = True

# Разрешаем все методы
CORS_ALLOW_ALL_METHODS = True

# Разрешаем все origins в режиме разработки
CORS_ALLOW_ALL_ORIGINS = True 