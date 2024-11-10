# File path: bots/main.py
# main.py

import asyncio
from aiogram import Bot, Dispatcher

from config import API_TOKEN
from handlers.callback_handlers import router as callback_router
from handlers.message_handlers import router as message_router
from handlers.state_handlers import router as state_router

from handlers.command_handlers import user_router as defuser_command_router
from handlers.command_handlers import router as user_command_router
from handlers.command_handlers import admin_router as admin_command_router
from data.database import Base, engine
from other.data_manager import auto_update_data


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    Base.metadata.create_all(engine)

    dp.include_router(defuser_command_router)
    dp.include_router(admin_command_router)
    dp.include_router(user_command_router)
    dp.include_router(callback_router)
    dp.include_router(message_router)
    dp.include_router(state_router)

    await bot.delete_webhook(drop_pending_updates=True)

    update_task = asyncio.create_task(auto_update_data())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())