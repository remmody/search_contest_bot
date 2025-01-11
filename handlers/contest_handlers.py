from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from bson import ObjectId

from handlers.responsible_handlers import show_responsible_list
from services.database import contests_col, users_col
from utils.file_utils import save_file
from config import logger
from datetime import datetime
import os

# Создаем роутер
router = Router()

# Хэндлер для добавления конкурса
@router.message(lambda message: message.text == "Добавить конкурс")
async def add_contest(message: types.Message):
    await message.answer("Введите название конкурса:")
    contests_col.update_one({"telegram_id": message.from_user.id}, {"$set": {"step": "name"}}, upsert=True)

# Хэндлер для обработки названия конкурса
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "name"}))
async def process_contest_name(message: types.Message):
    contests_col.update_one(
        {"telegram_id": message.from_user.id},
        {"$set": {"name": message.text, "step": "dates"}}
    )
    await message.answer("Введите даты проведения конкурса (в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ):")

# Хэндлер для обработки дат конкурса
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "dates"}))
async def process_contest_dates(message: types.Message):
    try:
        start_date_str, end_date_str = message.text.split(" - ")
        start_date = datetime.strptime(start_date_str.strip(), "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str.strip(), "%d.%m.%Y")

        if start_date > end_date:
            await message.answer("Дата начала не может быть позже даты окончания. Попробуйте снова.")
            return

        contests_col.update_one(
            {"telegram_id": message.from_user.id},
            {"$set": {"start_date": start_date, "end_date": end_date, "step": "description"}}
        )
        await message.answer("Введите описание конкурса:")
    except ValueError as e:
        logger.error(f"Ошибка при обработке даты: {e}")
        await message.answer("Некорректный формат дат. Пожалуйста, введите даты в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ.")

# Хэндлер для обработки описания конкурса
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "description"}))
async def process_contest_description(message: types.Message):
    contests_col.update_one(
        {"telegram_id": message.from_user.id},
        {"$set": {"description": message.text, "step": "file"}}
    )
    await message.answer("Прикрепите файл (pdf, docx, doc, xlsx):")

# Хэндлер для обработки файла
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "file"}))
async def process_contest_file(message: types.Message):
    if message.document:
        file_ext = message.document.file_name.split(".")[-1].lower()
        if file_ext not in ["pdf", "docx", "doc", "xlsx"]:
            await message.answer("Недопустимый формат файла. Разрешены только pdf, docx, doc, xlsx.")
            return

        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)  # Используем message.bot
        file_path = file.file_path
        file_name = message.document.file_name
        await message.bot.download_file(file_path, os.path.join("uploads", file_name))  # Используем message.bot
        contests_col.update_one(
            {"telegram_id": message.from_user.id},
            {"$set": {"file": file_name, "step": "responsible"}}
        )
        await message.answer("Файл успешно загружен. Теперь выберите ответственного за конкурс.")
        await show_responsible_list(message)
    else:
        await message.answer("Пожалуйста, прикрепите файл.")

# Хэндлер для отображения списка конкурсов
@router.message(lambda message: message.text == "Список конкурсов")
async def show_contests_list(message: types.Message):
    contests = list(contests_col.find({}).sort("start_date", 1))  # Сортировка по дате начала
    if not contests:
        await message.answer("Конкурсы не найдены.")
        return

    # Создание инлайн-клавиатуры с конкурсами
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for contest in contests:
        button_text = f"{contest['name']} ({contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')})"
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=button_text, callback_data=f"contest_{contest['_id']}")]
        )

    await message.answer("Список конкурсов:", reply_markup=keyboard)

# Хэндлер для обработки выбора конкурса
@router.callback_query(lambda query: query.data.startswith("contest_"))
async def process_contest_selection(query: types.CallbackQuery):
    contest_id = query.data.split("_")[1]
    try:
        # Преобразуем строку в ObjectId
        contest = contests_col.find_one({"_id": ObjectId(contest_id)})
        if not contest:
            await query.answer("Конкурс не найден.")
            return

        # Получаем имя ответственного
        responsible = users_col.find_one({"telegram_id": contest.get("responsible_id")})
        responsible_name = responsible["full_name"] if responsible else "Неизвестно"

        # Формируем сообщение с информацией о конкурсе
        contest_info = (
            f"Название: {contest['name']}\n"
            f"Описание: {contest['description']}\n"
            f"Даты проведения: {contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')}\n"
            f"Ответственный: {responsible_name}\n"
            f"Файл: {contest.get('file', 'Файл не прикреплен')}"
        )

        await query.message.answer(contest_info)

        # Если есть файл, отправляем его
        if contest.get("file"):
            file_path = os.path.join("uploads", contest["file"])
            if os.path.exists(file_path):  # Проверяем, существует ли файл
                try:
                    # Используем FSInputFile для отправки файла
                    file_to_send = FSInputFile(file_path)
                    await query.message.answer_document(file_to_send)
                except Exception as e:
                    logger.error(f"Не удалось отправить файл: {e}")
                    await query.message.answer("Произошла ошибка при отправке файла.")
            else:
                logger.error(f"Файл не найден: {file_path}")
                await query.message.answer("Файл не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обработке конкурса: {e}")
        await query.answer("Произошла ошибка при обработке конкурса.")