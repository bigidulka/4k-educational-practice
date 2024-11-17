from aiogram import types, BaseMiddleware
from keyboards.inline import *
from data.database import *

class UserTrackingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        username = event.from_user.username
        user = await get_user(user_id)
        
        if not user:
            user = await create_user(user_id, username)
        
        user_settings = await get_user_settings(user_id)
        if not user_settings:
            user_settings = await update_user_settings(user_id, BASE_SETTINGS)
        
        data['user_settings'] = await get_user_settings(user_id)
        
        return await handler(event, data)
