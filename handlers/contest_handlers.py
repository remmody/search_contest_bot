from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from bson import ObjectId

from handlers.responsible_handlers import show_responsible_list
from services.database import contests_col, users_col
from config import logger
from datetime import datetime
import os

# Создаем роутер
router = Router()


# Хэндлер для добавления конкурса
@router.message(lambda message: message.text == "Добавить конкурс")
async def add_contest(message: types.Message):
    # Создаем новый конкурс с уникальным _id
    contest_id = ObjectId()  # Уникальный идентификатор для нового конкурса
    contests_col.insert_one({
        "_id": contest_id,
        "telegram_id": message.from_user.id,
        "step": "name",
        "files": []
    })
    await message.answer("Введите название конкурса:")


# Хэндлер для обработки названия конкурса
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "name"}))
async def process_contest_name(message: types.Message):
    if not message.text:
        await message.answer("Пожалуйста, введите название конкурса текстом.")
        return
    # Обновляем конкурс, добавляя название
    contests_col.update_one(
        {"telegram_id": message.from_user.id, "step": "name"},
        {"$set": {"name": message.text, "step": "dates"}}
    )
    await message.answer("Введите даты проведения конкурса (в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ):")


@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "dates"}))
async def process_contest_dates(message: types.Message):
    # Проверяем, что сообщение содержит текст
    if not message.text:
        await message.answer("Пожалуйста, введите даты в текстовом формате.")
        return

    try:
        # Разделяем текст на две даты
        start_date_str, end_date_str = message.text.split(" - ")
        start_date = datetime.strptime(start_date_str.strip(), "%d.%m.%Y")
        end_date = datetime.strptime(end_date_str.strip(), "%d.%m.%Y")

        if start_date > end_date:
            await message.answer("Дата начала не может быть позже даты окончания. Попробуйте снова.")
            return

        # Обновляем конкурс, добавляя даты
        contests_col.update_one(
            {"telegram_id": message.from_user.id, "step": "dates"},
            {"$set": {"start_date": start_date, "end_date": end_date, "step": "description"}}
        )
        await message.answer("Введите описание конкурса:")
    except ValueError as e:
        logger.error(f"Ошибка при обработке даты: {e}")
        await message.answer("Некорректный формат дат. Пожалуйста, введите даты в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ.")


# Хэндлер для обработки описания конкурса
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "description"}))
async def process_contest_description(message: types.Message):
    if not message.text:
        await message.answer("Пожалуйста, введите описание конкурса текстом.")
        return
    # Обновляем конкурс, добавляя описание
    contests_col.update_one(
        {"telegram_id": message.from_user.id, "step": "description"},
        {"$set": {"description": message.text, "step": "file"}}
    )
    await message.answer("Прикрепите файл (pdf, docx, doc, xlsx). Чтобы закончить загрузку файлов, нажмите /done.")


# Хэндлер для обработки файла
@router.message(lambda message: contests_col.find_one({"telegram_id": message.from_user.id, "step": "file"}))
async def process_contest_file(message: types.Message):
    if message.document:
        file_ext = message.document.file_name.split(".")[-1].lower()
        if file_ext not in ["pdf", "docx", "doc", "xlsx"]:
            await message.answer("Недопустимый формат файла. Разрешены только pdf, docx, doc, xlsx.")
            return

        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        file_name = message.document.file_name
        await message.bot.download_file(file_path, os.path.join("uploads", file_name))

        # Добавляем файл в список файлов конкурса
        contests_col.update_one(
            {"telegram_id": message.from_user.id, "step": "file"},
            {"$push": {"files": file_name}}
        )
        await message.answer(f"Файл {file_name} успешно загружен. Прикрепите еще файлы или нажмите /done.")
    elif message.text == "/done":
        # Если пользователь нажал /done, завершаем загрузку файлов
        contest = contests_col.find_one({"telegram_id": message.from_user.id, "step": "file"})
        if contest:
            contests_col.update_one(
                {"telegram_id": message.from_user.id, "step": "file"},
                {"$set": {"step": "responsible"}}
            )
            await message.answer("Загрузка файлов завершена. Теперь выберите ответственного за конкурс.")
            await show_responsible_list(message)
    else:
        await message.answer("Пожалуйста, прикрепите файл или нажмите /done для завершения.")


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
        # Проверяем наличие обязательных полей
        if "name" in contest and "start_date" in contest and "end_date" in contest:
            button_text = f"{contest['name']} ({contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')})"
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=button_text, callback_data=f"contest_{contest['_id']}")]
            )
        else:
            logger.warning(f"Конкурс с _id {contest['_id']} пропущен из-за отсутствия обязательных полей.")

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

        # Проверяем наличие обязательных полей
        if "name" not in contest or "start_date" not in contest or "end_date" not in contest:
            await query.answer("Конкурс содержит неполные данные.")
            return

        # Получаем имя ответственного
        responsible = users_col.find_one({"telegram_id": contest.get("responsible_id")})
        responsible_name = responsible["full_name"] if responsible else "Неизвестно"

        # Формируем сообщение с информацией о конкурсе
        contest_info = (
            f"Название: {contest['name']}\n"
            f"Описание: {contest.get('description', 'Описание отсутствует')}\n"
            f"Даты проведения: {contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')}\n"
            f"Ответственный: {responsible_name}\n"
            f"Файлы: {', '.join(contest.get('files', [])) if contest.get('files') else 'Файлы не прикреплены'}"
        )

        # Создаем клавиатуру с кнопкой "Участвовать"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Участвовать", callback_data=f"join_{contest_id}")]
        ])

        await query.message.answer(contest_info, reply_markup=keyboard)

        # Если есть файлы, отправляем их
        if contest.get("files"):
            for file_name in contest["files"]:
                file_path = os.path.join("uploads", file_name)
                if os.path.exists(file_path):  # Проверяем, существует ли файл
                    try:
                        # Используем FSInputFile для отправки файла
                        file_to_send = FSInputFile(file_path)
                        await query.message.answer_document(file_to_send)
                    except Exception as e:
                        logger.error(f"Не удалось отправить файл {file_name}: {e}")
                        await query.message.answer(f"Произошла ошибка при отправке файла {file_name}.")
                else:
                    logger.error(f"Файл не найден: {file_path}")
                    await query.message.answer(f"Файл {file_name} не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обработке конкурса: {e}")
        await query.answer("Произошла ошибка при обработке конкурса.")


# Хэндлер для обработки нажатия на кнопку "Участвовать"
@router.callback_query(lambda query: query.data.startswith("join_"))
async def process_join_contest(query: types.CallbackQuery):
    contest_id = query.data.split("_")[1]
    user_id = query.from_user.id

    try:
        # Находим конкурс
        contest = contests_col.find_one({"_id": ObjectId(contest_id)})
        if not contest:
            await query.answer("Конкурс не найден.")
            return

        # Находим пользователя
        user = users_col.find_one({"telegram_id": user_id})
        if not user:
            await query.answer("Пользователь не найден.")
            return

        # Добавляем пользователя в список участников конкурса
        contests_col.update_one(
            {"_id": ObjectId(contest_id)},
            {"$addToSet": {"participants": user_id}}  # Используем $addToSet, чтобы избежать дубликатов
        )

        # Отправляем подтверждение пользователю
        await query.answer(f"Вы успешно присоединились к конкурсу {contest['name']}.")

        # Отправляем уведомление ответственному
        responsible_id = contest.get("responsible_id")
        if responsible_id:
            responsible = users_col.find_one({"telegram_id": responsible_id})
            if responsible:
                await query.bot.send_message(
                    responsible_id,
                    f"Новый участник конкурса:\n"
                    f"Название конкурса: {contest['name']}\n"
                    f"Даты проведения: {contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')}\n"
                    f"Участник: {user['full_name']}"
                )
    except Exception as e:
        logger.error(f"Ошибка при присоединении к конкурсу: {e}")
        await query.answer("Произошла ошибка при присоединении к конкурсу.")
