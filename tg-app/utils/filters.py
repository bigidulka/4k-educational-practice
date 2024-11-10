# utils/filters.py

from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.database import *
from other.data_manager import get_tokens
        
# class IsAdminFilter(BaseFilter):
#     async def __call__(self, event: Message) -> bool:
#         user_id = event.from_user.id
#         user = get_user(user_id)
#         return user.is_admin
    
# class IsValidTokenFilter(BaseFilter):
#     async def __call__(self, event: Message):
#         if event.text and event.text.startswith('#'):
#             token = event.text[1:].strip().upper()
#             tokens_data = get_tokens()
#             for full_token_key in tokens_data.keys():
#                 if full_token_key.startswith(token):
#                     return {'token': full_token_key}
#         return False