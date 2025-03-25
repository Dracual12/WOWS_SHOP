import json
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, FSInputFile
from aiogram.filters import Command
import bot.config as config
from bot.db import add_user, get_db_connection

# Настройка пути к проекту


# Инициализация бота и диспетчера
botik = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    add_user(telegram_id)
    photo = FSInputFile(f"{os.getcwd()}/bot/assets/welcome.jpeg")
    await botik.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=(
            f"Представляем новый обновленный бот от сервиса АРМАДА, где каждый игрок World of Warships: Legends сможет легко и быстро приобрести дублоны для своей учетной записи на любой платформе!\n\n"
            f"💥 Что нового?\n"
            " - Удобный интерфейс, который делает процесс покупки еще проще.\n"
            "- Полная совместимость с PlayStation, Xbox и другими платформами.\n"
            "- Быстрая доставка дублонов — вы получите их мгновенно!\n\n"
            f"🎯 Почему выбирают нас?\n"
            f"- Надежность и безопасность — ваша учетная запись в полной сохранности.\n"
            f"- Доступные цены и регулярные акции для наших клиентов.\n"
            f"- Поддержка 24/7 — мы всегда готовы помочь!\n\n"
            f"Погрузитесь в морские сражения с максимальными возможностями, приобретая дублоны в нашем обновленном боте! ⚓"
        ),
        reply_markup=main_menu()
    )

# Главное меню
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))],
        [InlineKeyboardButton(text="\U0001F4DD Отзывы", url="https://t.me/armada_feedback")],
        [InlineKeyboardButton(text="\U0001F4E9 Задать вопрос", url="https://t.me/armada_support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Запуск бота
async def main():
    await dp.start_polling(botik)

if __name__ == "__main__":
    asyncio.run(main())