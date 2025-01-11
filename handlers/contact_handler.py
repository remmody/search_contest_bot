from aiogram import Router, types
from services.database import users_col
from utils.role_utils import send_role_keyboard

# Создаем роутер
router = Router()


# Хэндлер для получения контакта (номер телефона)
@router.message(lambda message: message.contact is not None)
async def contact_handler(message: types.Message):
    if not message.contact or message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте свой собственный номер телефона.")
        return

    users_col.update_one(
        {"telegram_id": message.from_user.id},
        {"$set": {"phone": message.contact.phone_number, "role": "teacher"}},
        upsert=True
    )

    await message.answer("Спасибо! Теперь введите ваше полное имя (ФИО).")
    await send_role_keyboard(message.bot, message.from_user.id, "teacher")