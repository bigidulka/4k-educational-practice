from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.attributes import flag_modified
from functools import reduce
from operator import getitem
from copy import deepcopy
from config import DATABASE_URL, BASE_SETTINGS

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    settings = relationship("Settings", back_populates="user")

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    settings = Column(JSON)
    user = relationship("User", back_populates="settings")

async def get_user(user_id: int) -> User:
    async with AsyncSessionLocal() as session:
        return await session.get(User, user_id)

async def create_user(user_id: int, username: str) -> User:
    async with AsyncSessionLocal() as session:
        user = User(id=user_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_username(user_id: int) -> str:
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        return user.username if user else None

async def get_all_users() -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return [{'id': user.id, 'username': user.username} for user in users]

async def get_user_settings(user_id: int):
    async with AsyncSessionLocal() as session:
        user_settings = await session.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        user_settings = user_settings.scalars().first()
        if user_settings:
            complete_settings = merge_settings(BASE_SETTINGS, user_settings.settings)
            if user_settings.settings != complete_settings:
                user_settings.settings = complete_settings
                flag_modified(user_settings, "settings")
                await session.commit()
        else:
            user_settings = Settings(user_id=user_id, settings=BASE_SETTINGS)
            session.add(user_settings)
            await session.commit()
            return BASE_SETTINGS
        return complete_settings

def merge_settings(base: dict, user: dict) -> dict:
    merged_settings = deepcopy(base)

    def recursive_update(base_dict, user_dict):
        for key, value in user_dict.items():
            if isinstance(value, dict) and key in base_dict:
                recursive_update(base_dict[key], value)
            else:
                base_dict[key] = value

    recursive_update(merged_settings, user)
    return merged_settings

async def update_user_settings(user_id: int, new_settings: dict):
    async with AsyncSessionLocal() as session:
        user_settings = await session.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        user_settings = user_settings.scalars().first()
        if not user_settings:
            user_settings = Settings(user_id=user_id, settings=new_settings)
            session.add(user_settings)
        else:
            user_settings.settings = new_settings
        flag_modified(user_settings, "settings")
        await session.commit()

async def update_specific_user_settings(user_id: int, updates: dict):
    async with AsyncSessionLocal() as session:
        user_settings = await session.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        user_settings = user_settings.scalars().first()
        if user_settings:
            for key, value in updates.items():
                user_settings.settings[key] = value
            flag_modified(user_settings, "settings")
            await session.commit()

async def add_item_to_user_list_setting(user_id: int, list_path: list, new_item):
    async with AsyncSessionLocal() as session:
        user_settings = await session.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        user_settings = user_settings.scalars().first()
        if user_settings:
            settings = user_settings.settings
            target_list = reduce(getitem, list_path, settings)
            if new_item not in target_list:
                target_list.append(new_item)
                flag_modified(user_settings, "settings")
                await session.commit()
                return True
            else:
                return False

async def remove_item_from_user_list_setting(user_id: int, list_path: list, item_to_remove):
    async with AsyncSessionLocal() as session:
        user_settings = await session.execute(
            select(Settings).where(Settings.user_id == user_id)
        )
        user_settings = user_settings.scalars().first()
        if user_settings:
            settings = user_settings.settings
            target_list = reduce(getitem, list_path, settings)
            if item_to_remove in target_list:
                target_list.remove(item_to_remove)
                flag_modified(user_settings, "settings")
                await session.commit()
                return True
            else:
                return False
