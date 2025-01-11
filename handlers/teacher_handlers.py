# from aiogram import Router, types
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from services.database import contests_col
#
# # Создаем роутер
# router = Router()
#
# # Хэндлер для отображения списка конкурсов
# @router.message(lambda message: message.text == "Список конкурсов")
# async def show_contests_list(message: types.Message):
#     contests = list(contests_col.find({}).sort("start_date", 1))  # Сортировка по дате начала
#     if not contests:
#         await message.answer("Конкурсы не найдены.")
#         return
#
#     # Создание инлайн-клавиатуры с конкурсами
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[])
#     for contest in contests:
#         button_text = f"{contest['name']} ({contest['start_date'].strftime('%d.%m.%Y')} - {contest['end_date'].strftime('%d.%m.%Y')})"
#         keyboard.inline_keyboard.append(
#             [InlineKeyboardButton(text=button_text, callback_data=f"contest_{contest['_id']}")]
#         )
#
#     await message.answer("Список конкурсов:", reply_markup=keyboard)