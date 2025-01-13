from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import users_col

async def show_user_list(message: types.Message, role: str):
    # Фильтруем пользователей, у которых есть поле full_name
    users = list(users_col.find({"full_name": {"$exists": True}}).sort("full_name", 1))
    if not users:
        await message.answer("Пользователи не найдены.")
        return

    # Группировка пользователей по первой букве фамилии
    user_dict = {}
    for user in users:
        if "full_name" in user and user["full_name"]:  # Проверяем наличие и непустое значение
            first_letter = user["full_name"][0].upper()
            if first_letter not in user_dict:
                user_dict[first_letter] = []
            user_dict[first_letter].append(user)

    # Создание инлайн-клавиатуры с буквами
    letters = sorted(user_dict.keys())
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    for letter in letters:
        row.append(InlineKeyboardButton(text=letter, callback_data=f"letter_{letter}_{role}"))
        if len(row) == 5:  # 5 кнопок в строке
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)

    await message.answer("Выберите первую букву фамилии преподавателя:", reply_markup=keyboard)