from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_phone_keyboard():
    phone_button = KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
    phone_keyboard = ReplyKeyboardMarkup(keyboard=[[phone_button]], resize_keyboard=True)
    return phone_keyboard