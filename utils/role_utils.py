from aiogram import Bot
from keyboards import admin_keyboard, responsible_keyboard, teacher_keyboard


async def send_role_keyboard(bot: Bot, user_id: int, role: str):
    if role == "admin":
        keyboard = await admin_keyboard.create_admin_keyboard()
    elif role == "responsible":
        keyboard = await responsible_keyboard.create_responsible_keyboard()
    else:
        keyboard = await teacher_keyboard.create_teacher_keyboard()

    await bot.send_message(
        user_id,
        "Ваши возможности обновлены в соответствии с вашей новой ролью.",
        reply_markup=keyboard
    )