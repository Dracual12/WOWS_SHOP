import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.append(project_root)

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, FSInputFile
from aiogram.filters import Command
import asyncio
import bot.config as config
import os
from bot.db import add_user
import requests

from bot.db import get_db_connection



botik = Bot(token=config.BOT_TOKEN)
async def get_link(user):
    conn = get_db_connection()
    last_order = conn.execute('SELECT id FROM orders WHERE user_id = ?', (user,)).fetchone()
    print(last_order)
    order_id = int(last_order['id'])
    last_cart = conn.execute('SELECT cart FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    cart = int(last_cart['cart']['total'])
    conn.close()
    url = f"https://alfa.rbsuat.com/payment/rest/register.do?token=157t7528u3o9bg0o9rljvu7dqs&orderNumber={order_id}&amount={cart}&returnUrl=192.168.0.1"
    await botik.send_message(user, url)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    add_user(telegram_id)
    with open(f"{os.getcwd()}/assets/welcome.jpeg", "rb") as image:
        photo = FSInputFile(f"{os.getcwd()}/assets/welcome.jpeg")
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

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))],
        [InlineKeyboardButton(text="\U0001F4DD Отзывы", url="https://t.me/armada_feedback")],
        [InlineKeyboardButton(text="\U0001F4E9 Задать вопрос", url="https://t.me/armada_support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



async def send_link(message:types.Message):
    await botik.send_message(chat_id=message.from_user.id, text=f'Ссфылка на оплату: {get_link()}')



async def main():
    await dp.start_polling(botik)

if __name__ == "__main__":
    asyncio.run(main())
