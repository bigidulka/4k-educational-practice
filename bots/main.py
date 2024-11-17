import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from handlers.callback_handlers import router as callback_router
from handlers.state_handlers import router as state_router
from handlers.command_handlers import router as user_command_router
from data.database import Base, engine
from other.sending_notifications import start as notify_task_start

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp.include_router(user_command_router)
    dp.include_router(callback_router)
    dp.include_router(state_router)

    await bot.delete_webhook(drop_pending_updates=True)
    
    notify_task  = asyncio.create_task(notify_task_start(bot))
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())