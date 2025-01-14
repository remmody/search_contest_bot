from aiogram import BaseMiddleware
from aiogram.types import Message
from services.database import users_col

class RoleMiddleware(BaseMiddleware):
    def __init__(self, allowed_roles: list[str]):
        super().__init__()
        self.allowed_roles = allowed_roles

    async def __call__(self, handler, event: Message, data: dict):
        user = users_col.find_one({"telegram_id": event.from_user.id})
        if user and user.get("role") in self.allowed_roles:
            return await handler(event, data)
        await event.answer("У вас нет прав для выполнения этого действия.")
