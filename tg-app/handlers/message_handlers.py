# handlers/message_handlers.py

from aiogram import Router
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from keyboards.inline import *
from other.data_manager import get_tokens
from utils.utils import form_telegram_message
from utils.middlewares import UserTrackingMiddleware, SubscriptionMiddleware 
from utils.filters import IsValidTokenFilter
from data.database import *

router = Router()
router.message.outer_middleware(UserTrackingMiddleware())
router.message.outer_middleware(SubscriptionMiddleware())

@router.message(IsValidTokenFilter())
async def handle_token_message(message: types.Message, state: FSMContext, token: str, user_settings):
    tokens_data = get_tokens()
    await state.update_data(tokens_data=tokens_data)
    
    data = tokens_data.get(token)
    
    if data:
        long_list = user_settings.get('long_list', [])
        short_list = user_settings.get('short_list', [])
        
        token_message = form_telegram_message(data, token)

        if token in long_list:
            token_message += "\n🥬 В Лонг листе"
        if token in short_list:
            token_message += "\n🍁 В Шорт листе"

        await message.answer(text=token_message, reply_markup=token_selection_keyboard(token))
    else:
        await message.answer("Монета не найдена.")