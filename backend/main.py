from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import CORS_ALLOWED_ORIGINS, DEBUG
from users.routes import router as users_router
from books.routes import router as books_router
from achievements.routes import router as achievements_router

app = FastAPI(
    title="Reader API",
    description="API для приложения Reader",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS if not DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(books_router, prefix="/api", tags=["books"])
app.include_router(achievements_router, prefix="/api", tags=["achievements"])

@app.get("/")
async def root():
    return {"message": "Welcome to Reader API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 