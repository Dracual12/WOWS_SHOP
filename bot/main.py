from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputFile, FSInputFile
from aiogram.filters import Command
import asyncio
import asyncio
import config
import os
from db import add_user

bot = Bot(token=config.BOT_TOKEN)

dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    add_user(telegram_id)
    with open(f"{os.getcwd()}/assets/welcome_image.jpeg", "rb") as image:
        photo = FSInputFile(f"{os.getcwd()}/assets/welcome_image.jpeg")
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=(
                f"Представляем новый обновленный бот от сервиса <>, где каждый игрок World of Warships: Legends сможет легко и быстро приобрести дублоны для своей учетной записи на любой платформе!\n\n"

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

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))],
        [InlineKeyboardButton(text="\U0001F4DD Отзывы", url="https://t.me/armada_feedback")],
        #[InlineKeyboardButton(text="\U0001F4E9 Задать вопрос", url="@armada_support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

asyncio.run(main())