from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from decimal import *
import os
import time
import asyncio
from aiogram.types import Message, FSInputFile
import base64
from config import TIMEFRAMES
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from utils.states import FilterStates
from keyboards.inline import filter_editor_keyboard
from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Optional

async def delete_message(message, state):
    await message.delete()
    state_data = await state.get_data()
    chat_id = state_data.get('chat_id')
    message_id = state_data.get('message_id')
    await message.bot.delete_message(chat_id, message_id)

def handle_telegram_exception(func):
    async def wrapper(call: types.CallbackQuery, *args, **kwargs):
        try:
            response = await func(call, *args, **kwargs)
            await call.answer()
            return response
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await call.answer('Изменений нет.')
            else:
                print(f"Другая ошибка Telegram API: {e}")
                await call.answer()
    return wrapper