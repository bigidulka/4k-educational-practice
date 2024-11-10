from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref  # Импортируем backref
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timedelta
from functools import reduce
from operator import getitem
from copy import deepcopy

from config import *

Base = declarative_base()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    is_subscribed = Column(Boolean, default=False)
    subscription_end = Column(DateTime, default=None)
    filters = relationship("Filter", back_populates="user")
    is_admin = Column(Boolean, default=False)

class Filter(Base):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    settings = Column(JSON)
    user = relationship("User", back_populates="filters")

class NotificationLog(Base):
    __tablename__ = 'notification_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    message_type = Column(String, nullable=False)
    key_info = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", backref=backref("notification_logs", cascade="all, delete-orphan"))
    
# подписка
def check_user_subscription(user_id: int) -> bool:
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user and user.is_subscribed:
            return user.subscription_end > datetime.utcnow()
        return False
    
def get_users_ids_with_subscription_or_admin() -> list:
    with SessionLocal() as session:
        current_time = datetime.utcnow()
        users = session.query(User).filter(
            (User.is_subscribed == True) & (User.subscription_end > current_time) | (User.is_admin == True)
        ).all()
        return [user.id for user in users]
    
def grant_subscription(user_id: int, days: int):
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            if user.subscription_end and user.subscription_end > datetime.utcnow():
                user.subscription_end += timedelta(days=days)
            else:
                user.subscription_end = datetime.utcnow() + timedelta(days=days)
            user.is_subscribed = True
            session.commit()

def revoke_subscription(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.is_subscribed = False
            user.subscription_end = None
            session.commit()

def get_all_subscribed_users():
    with SessionLocal() as session:
        current_time = datetime.utcnow()
        users = session.query(User).filter(
            User.is_subscribed == True,
            User.subscription_end > current_time
        ).all()
        return [{'id': user.id, 'username': user.username, 'subscription_end': user.subscription_end} for user in users]

# пользователь
def get_user(user_id: int) -> User:
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        return user

def create_user(user_id: int, username: str) -> User:
    with SessionLocal() as session:
        user = User(
            id=user_id,
            username=username,
            is_subscribed=False,
            subscription_end=None
        )
        session.add(user)
        session.commit()
        return user
    
def get_username(user_id: int) -> str:
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            return user.username
        return None

def get_all_users() -> list:
    with SessionLocal() as session:
        users = session.query(User).all()
        return [{'id': user.id, 'username': user.username} for user in users]
    
def get_users_with_notifications_enabled_ids() -> list:
    with SessionLocal() as session:
        users_with_filters = session.query(User).join(Filter).all()
        return [user.id for user in users_with_filters if user.filters[0].settings.get('notifications', False)]
    
# настройки
def get_user_settings(user_id: int):
    with SessionLocal() as session:
        user_filter = session.query(Filter).filter(Filter.user_id == user_id).first()
        if user_filter:
            complete_settings = merge_settings(BASE_SETTINGS, user_filter.settings)
            
            if user_filter.settings != complete_settings:
                user_filter.settings = complete_settings
                flag_modified(user_filter, "settings")
                session.commit()
        else:
            user_filter = Filter(user_id=user_id, settings=BASE_SETTINGS)
            session.add(user_filter)
            session.commit()
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
    
def update_user_settings(user_id: int, new_settings: dict):
    with SessionLocal() as session:
        user_filter = session.query(Filter).filter(Filter.user_id == user_id).first()
        if not user_filter:
            user_filter = Filter(user_id=user_id, settings=new_settings)
            session.add(user_filter)
        else:
            user_filter.settings = new_settings
        flag_modified(user_filter, "settings")
        session.commit()
     
def update_specific_user_settings(user_id: int, updates: dict):
    with SessionLocal() as session:
        user_filter = session.query(Filter).filter_by(user_id=user_id).first()
        def recursive_update(orig_dict, new_dict):
            for key, value in new_dict.items():
                if isinstance(value, dict) and key in orig_dict:
                    recursive_update(orig_dict[key], value)
                else:
                    orig_dict[key] = value

        recursive_update(user_filter.settings, updates)
        flag_modified(user_filter, "settings")
        session.commit()
            
def add_item_to_user_list_setting(user_id: int, list_path: list, new_item):
    with SessionLocal() as session:
        user_filter = session.query(Filter).filter_by(user_id=user_id).first()
        settings = user_filter.settings
        target_list = reduce(getitem, list_path, settings)
        if new_item not in target_list:
            target_list.append(new_item)
            flag_modified(user_filter, "settings")
            session.commit()
            return True
        else:
            return False
        
def remove_item_from_user_list_setting(user_id: int, list_path: list, item_to_remove):
    with SessionLocal() as session:
        user_filter = session.query(Filter).filter_by(user_id=user_id).first()
        if user_filter:
            settings = user_filter.settings
            target_list = reduce(getitem, list_path, settings)
            if item_to_remove in target_list:
                target_list.remove(item_to_remove)
                flag_modified(user_filter, "settings")
                session.commit()
                return True
            else:
                return False
        
# админка
def grant_admin(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.is_admin = True
            session.commit()

def revoke_admin(user_id: int):
    with SessionLocal() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.is_admin = False
            session.commit()