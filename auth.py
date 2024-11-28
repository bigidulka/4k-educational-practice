# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.future import select
from passlib.context import CryptContext
import sqlalchemy
import uvicorn
from typing import Optional
from datetime import datetime, timedelta
import secrets

# Настройка базы данных
DATABASE_URL = "sqlite+aiosqlite:///./users.db"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Модель избранного актива
class FavoriteAsset(Base):
    __tablename__ = 'favorite_assets'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    asset_type = Column(String, nullable=False)  # Тип актива: "stock", "crypto", "currency"
    asset_identifier = Column(String, nullable=False)  # Уникальный идентификатор актива (например, тикер)
    name = Column(String, nullable=False)  # Название актива

# Модель для сброса пароля
class PasswordResetCode(Base):
    __tablename__ = 'password_reset_codes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

# Создание таблиц
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Pydantic схемы
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_repeat: str

class UserLogin(BaseModel):
    username: str
    password: str

class FavoriteAssetCreate(BaseModel):
    asset_type: str
    asset_identifier: str
    name: str

class FavoriteAssetResponse(BaseModel):
    id: int
    asset_type: str
    asset_identifier: str
    name: str

class PasswordResetRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class PasswordResetConfirm(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    code: str
    new_password: str
    new_password_repeat: str

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_reset_code(length=6):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

# Инициализация FastAPI
app = FastAPI()

# Зависимость для получения сессии
async def get_session():
    async with async_session() as session:
        yield session

# Регистрация пользователя
@app.post("/register")
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    if user.password != user.password_repeat:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Проверка на существование пользователя
    result = await session.execute(
        sqlalchemy.select(User).where((User.email == user.email) | (User.username == user.username))
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"message": "Пользователь зарегистрирован успешно"}

# Логин пользователя
@app.post("/login")
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        sqlalchemy.select(User).where(User.username == user.username)
    )
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверные учетные данные")
    
    return {"message": "Успешный вход", "user_id": db_user.id}

# Запрос сброса пароля
@app.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, session: AsyncSession = Depends(get_session)):
    if not request.email and not request.username:
        raise HTTPException(status_code=400, detail="Необходимо предоставить email или логин")

    # Поиск пользователя
    query = sqlalchemy.select(User)
    if request.email:
        query = query.where(User.email == request.email)
    elif request.username:
        query = query.where(User.username == request.username)

    result = await session.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Генерация кода и установка срока действия (например, 10 минут)
    code = generate_reset_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Удаление предыдущих кодов для пользователя
    await session.execute(
        sqlalchemy.delete(PasswordResetCode).where(PasswordResetCode.user_id == user.id)
    )

    # Сохранение нового кода
    reset_code = PasswordResetCode(
        user_id=user.id,
        code=code,
        expires_at=expires_at
    )
    session.add(reset_code)
    await session.commit()

    # В реальном приложении здесь нужно отправить код пользователю (например, по email)
    # Но поскольку вы хотите отправлять код непосредственно в приложение, возвращаем его в ответе
    return {"message": "Код сброса пароля отправлен", "reset_code": code}

# Подтверждение сброса пароля
@app.post("/reset-password")
async def reset_password(request: PasswordResetConfirm, session: AsyncSession = Depends(get_session)):
    if not request.email and not request.username:
        raise HTTPException(status_code=400, detail="Необходимо предоставить email или логин")
    
    if request.new_password != request.new_password_repeat:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Поиск пользователя
    query = sqlalchemy.select(User)
    if request.email:
        query = query.where(User.email == request.email)
    elif request.username:
        query = query.where(User.username == request.username)
    
    result = await session.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Поиск кода сброса пароля
    result = await session.execute(
        sqlalchemy.select(PasswordResetCode).where(
            (PasswordResetCode.user_id == user.id) &
            (PasswordResetCode.code == request.code)
        )
    )
    reset_code = result.scalars().first()
    
    if not reset_code:
        raise HTTPException(status_code=400, detail="Неверный код сброса пароля")
    
    if reset_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Код сброса пароля истек")
    
    # Обновление пароля
    user.hashed_password = get_password_hash(request.new_password)
    await session.delete(reset_code)  # Удаление использованного кода
    await session.commit()
    
    return {"message": "Пароль успешно изменен"}

# Добавление избранного актива
@app.post("/favorites", response_model=FavoriteAssetResponse)
async def add_favorite_asset(
    favorite: FavoriteAssetCreate,
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, не добавлен ли актив уже в избранное
    result = await session.execute(
        select(FavoriteAsset).where(
            (FavoriteAsset.user_id == user_id) &
            (FavoriteAsset.asset_identifier == favorite.asset_identifier) &
            (FavoriteAsset.asset_type == favorite.asset_type)
        )
    )
    existing_asset = result.scalars().first()
    if existing_asset:
        raise HTTPException(status_code=400, detail="Актив уже в избранном")

    # Добавляем актив в избранное
    new_favorite = FavoriteAsset(
        user_id=user_id,
        asset_type=favorite.asset_type,
        asset_identifier=favorite.asset_identifier,
        name=favorite.name
    )
    session.add(new_favorite)
    await session.commit()
    await session.refresh(new_favorite)
    return new_favorite

# Удаление избранного актива
@app.delete("/favorites/{asset_id}")
async def remove_favorite_asset(asset_id: int, user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(FavoriteAsset).where(
            (FavoriteAsset.id == asset_id) & (FavoriteAsset.user_id == user_id)
        )
    )
    favorite = result.scalars().first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Актив не найден в избранном")
    
    await session.delete(favorite)
    await session.commit()
    return {"message": "Актив удален из избранного"}

# Получение списка избранных активов
@app.get("/favorites", response_model=list[FavoriteAssetResponse])
async def get_favorite_assets(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(FavoriteAsset).where(FavoriteAsset.user_id == user_id)
    )
    favorites = result.scalars().all()
    if not favorites:
        return []  # Возвращаем пустой список, если нет избранных активов
    return favorites

# Запуск и инициализация
@app.on_event("startup")
async def on_startup():
    await init_models()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
