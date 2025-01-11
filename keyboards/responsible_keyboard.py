from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def create_responsible_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Уведомления о новых конкурсах"), KeyboardButton(text="Уведомления о заявках на участие")],
            [KeyboardButton(text="Список конкурсов"), KeyboardButton(text="Список преподавателей")]
        ],
        resize_keyboard=True
    )
    return keyboard