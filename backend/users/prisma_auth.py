from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from prisma import Prisma
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .schemas import UserCreate, User

# Настройки JWT
SECRET_KEY = "your-secret-key"  # В продакшене использовать переменные окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PrismaAuth:
    def __init__(self):
        self.prisma = Prisma()

    async def connect(self):
        await self.prisma.connect()

    async def disconnect(self):
        await self.prisma.disconnect()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.prisma.user.find_unique(where={'email': email})
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await self.prisma.user.find_unique(where={'email': email})
        if user is None:
            raise credentials_exception
        return user

    async def create_user(self, user: UserCreate) -> User:
        hashed_password = self.get_password_hash(user.password)
        db_user = await self.prisma.user.create(
            data={
                "email": user.email,
                "hashed_password": hashed_password,
                "full_name": user.full_name,
                "is_active": True,
                "is_superuser": False
            }
        )
        return db_user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.prisma.user.find_unique(where={'email': email})

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        return await self.prisma.user.update(
            where={'id': user_id},
            data=user_data
        )

    async def delete_user(self, user_id: int) -> Optional[User]:
        return await self.prisma.user.delete(where={'id': user_id})

    async def get_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        return await self.prisma.user.find_many(
            skip=skip,
            take=limit,
            order_by={'created_at': 'desc'}
        ) 