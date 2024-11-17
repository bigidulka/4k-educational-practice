from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import asyncio

from data.database import *
from utils.middlewares import UserTrackingMiddleware
from keyboards.inline import *

router = Router()
router.message.outer_middleware(UserTrackingMiddleware())

def get_main_menu_reply_keyboard():
    kb = [
        [KeyboardButton(text="Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

@router.message(CommandStart())
async def show_main_menu(message: Message):
    message_text, inline_keyboard = main_menu_keyboard()
    reply_keyboard = get_main_menu_reply_keyboard()
    await message.answer(
        text=message_text,
        reply_markup=inline_keyboard
    )
    await message.answer(
        text="Выберите действие:",
        reply_markup=reply_keyboard
    )
    
@router.message(F.text == "Главное меню")
async def handle_main_menu(message: Message):
    message_text, inline_keyboard = main_menu_keyboard()
    reply_keyboard = get_main_menu_reply_keyboard()
    await message.answer(
        text=message_text,
        reply_markup=inline_keyboard
    )