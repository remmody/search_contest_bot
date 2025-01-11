from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database import users_col, contests_col
from config import logger

# Создаем роутер
router = Router()

# Хэндлер для отображения списка ответственных
@router.message(lambda message: message.text == "Список ответственных")
async def show_responsible_list(message: types.Message):
    responsibles = list(users_col.find({"role": "responsible"}).sort("full_name", 1))
    if not responsibles:
        await message.answer("Ответственные не найдены.")
        return

    # Создание инлайн-клавиатуры с ответственными
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for responsible in responsibles:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=responsible["full_name"],
                                                              callback_data=f"responsible_{responsible['telegram_id']}")])

    await message.answer("Выберите ответственного за конкурс:", reply_markup=keyboard)

# Хэндлер для обработки выбора ответственного
@router.callback_query(lambda query: query.data.startswith("responsible_"))
async def process_responsible_selection(query: types.CallbackQuery):
    responsible_id = int(query.data.split("_")[1])  # Получаем ID ответственного

    # Находим текущий конкурс, который добавляется
    contest = contests_col.find_one({"telegram_id": query.from_user.id, "step": "responsible"})
    if not contest:
        await query.answer("Конкурс не найден.")
        return

    # Обновляем конкурс, добавляя ID ответственного
    contests_col.update_one(
        {"_id": contest["_id"]},
        {"$set": {"responsible_id": responsible_id, "step": None}}  # Завершаем шаг
    )

    # Получаем имя ответственного
    responsible = users_col.find_one({"telegram_id": responsible_id})
    responsible_name = responsible["full_name"] if responsible else "Неизвестно"

    await query.answer(f"Ответственный {responsible_name} успешно назначен.")
    await query.message.edit_text(f"Ответственный {responsible_name} назначен за конкурс.")