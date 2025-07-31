from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from .prisma_auth import PrismaAuth, ACCESS_TOKEN_EXPIRE_MINUTES
from .schemas import User, UserCreate, Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth = PrismaAuth()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    db_user = await auth.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return await auth.create_user(user=user)

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user

@router.get("/users/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100):
    users = await auth.get_users(skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: dict,
    current_user: User = Depends(auth.get_current_user)
):
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_user = await auth.update_user(user_id=user_id, user_data=user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/users/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    current_user: User = Depends(auth.get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    deleted_user = await auth.delete_user(user_id=user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return deleted_user 