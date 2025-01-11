from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def create_teacher_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Список конкурсов"), KeyboardButton(text="Уведомления о новых конкурсах")]
        ],
        resize_keyboard=True
    )
    return keyboard