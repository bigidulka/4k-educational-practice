from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.filters.command import CommandObject

from data.database import *
from keyboards.inline import *
from utils.middlewares import UserTrackingMiddleware

router = Router()
router.message.outer_middleware(UserTrackingMiddleware())

@router.message(CommandStart())
async def show_main_menu(message: Message):
    message_text, reply_markup = main_menu_keyboard()  
    await message.answer(
        text=message_text,
        reply_markup=reply_markup
    )