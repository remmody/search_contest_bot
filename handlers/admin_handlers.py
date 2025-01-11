from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import logger
from services.database import users_col
from utils.user_utils import show_user_list
from utils.role_utils import send_role_keyboard  # Импортируем функцию

# Создаем роутер
router = Router()

# Хэндлер для добавления администратора
@router.message(lambda message: message.text == "Добавить администратора")
async def add_admin(message: types.Message):
    await show_user_list(message, "admin")

# Хэндлер для добавления ответственного
@router.message(lambda message: message.text == "Добавить ответственного")
async def add_responsible(message: types.Message):
    await show_user_list(message, "responsible")

# Хэндлер для добавления преподавателя
@router.message(lambda message: message.text == "Добавить преподавателя")
async def add_teacher(message: types.Message):
    await show_user_list(message, "teacher")

# Хэндлер для обработки выбора буквы
@router.callback_query(lambda query: query.data.startswith("letter_"))
async def process_letter_selection(query: types.CallbackQuery):
    _, letter, role = query.data.split("_")
    users = list(users_col.find({"full_name": {"$regex": f"^{letter}", "$options": "i"}}).sort("full_name", 1))
    if not users:
        await query.answer("Пользователи не найдены.")
        return

    # Создание инлайн-клавиатуры с пользователями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for user in users:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=user["full_name"], callback_data=f"user_{user['telegram_id']}_{role}")]
        )

    await query.message.edit_text(f"Преподаватели, фамилии которых начинаются на {letter}:", reply_markup=keyboard)

# Хэндлер для обработки выбора пользователя
@router.callback_query(lambda query: query.data.startswith("user_"))
async def process_user_selection(query: types.CallbackQuery):
    _, user_id, role = query.data.split("_")
    user_id = int(user_id)

    # Проверка, является ли пользователь администратором
    user = users_col.find_one({"telegram_id": user_id})
    if user and user.get("role") == "admin":
        await query.answer("Нельзя изменить роль администратора.")
        return

    # Обновление роли пользователя
    users_col.update_one({"telegram_id": user_id}, {"$set": {"role": role}})
    await query.answer(f"Роль '{role}' успешно назначена пользователю.")

    # Уведомление пользователя о новой роли
    try:
        await query.bot.send_message(user_id, f"Вам назначена новая роль: {role}.")  # Используем query.bot
        # Отправляем пользователю новую клавиатуру в соответствии с его ролью
        await send_role_keyboard(query.bot, user_id, role)  # Передаем query.bot
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await query.message.edit_text(f"Роль '{role}' назначена пользователю.")