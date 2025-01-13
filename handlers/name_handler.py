from aiogram import Router, types
from services.database import users_col

# Создаем роутер
router = Router()

# Хэндлер для получения ФИО
@router.message(lambda message: users_col.find_one(
    {"telegram_id": message.from_user.id, "phone": {"$exists": True}, "full_name": None}))
async def name_handler(message: types.Message):
    if not message.text:
        await message.answer("Пожалуйста, введите ваше полное имя (ФИО).")
        return

    users_col.update_one(
        {"telegram_id": message.from_user.id},
        {"$set": {"full_name": message.text}}
    )
    await message.answer("Ваши данные сохранены. Дождитесь назначения роли администратором или ответственным.")