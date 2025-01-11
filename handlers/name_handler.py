from aiogram import Router, types
from services.database import users_col
from utils.role_utils import send_role_keyboard

# Создаем роутер
router = Router()

# Хэндлер для получения ФИО
@router.message(lambda message: users_col.find_one(
    {"telegram_id": message.from_user.id, "phone": {"$exists": True}, "full_name": None}))
async def name_handler(message: types.Message):
    users_col.update_one(
        {"telegram_id": message.from_user.id},
        {"$set": {"full_name": message.text}}
    )
    await message.answer("Ваши данные сохранены. Дождитесь назначения роли администратором или ответственным.")
    await send_role_keyboard(message.bot, message.from_user.id, "teacher")