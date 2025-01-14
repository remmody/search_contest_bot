from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить создание конкурса")]
        ],
        resize_keyboard=True
    )
    return keyboard