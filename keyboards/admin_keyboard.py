from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def create_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить администратора"), KeyboardButton(text="Добавить ответственного")],
            [KeyboardButton(text="Добавить преподавателя"), KeyboardButton(text="Добавить конкурс")],
            [KeyboardButton(text="Список конкурсов"), KeyboardButton(text="Список ответственных")],
            [KeyboardButton(text="Список преподавателей"), KeyboardButton(text="Редактировать имя пользователя")]
        ],
        resize_keyboard=True
    )
    return keyboard