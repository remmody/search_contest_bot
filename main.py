from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import logger  # Импортируем только logger
import os

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN в переменных окружения.")

bot = Bot(token=BOT_TOKEN)  # Инициализируем бота

# Диспетчер
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Импортируем роутеры из хэндлеров
from handlers import start_handler, contact_handler, name_handler, admin_handlers, responsible_handlers, teacher_handlers, contest_handlers

# Подключаем роутеры к диспетчеру
dp.include_router(start_handler.router)
dp.include_router(contact_handler.router)
dp.include_router(name_handler.router)
dp.include_router(admin_handlers.router)
dp.include_router(responsible_handlers.router)
# dp.include_router(teacher_handlers.router)
dp.include_router(contest_handlers.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())