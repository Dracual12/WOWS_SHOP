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

def pay(link):
    buttons =  [
        [InlineKeyboardButton(text="Оплатить", url=link)],
        [InlineKeyboardButton(text="Пользовательское соглашение", url="https://clck.ru/3GgzNq"),
        InlineKeyboardButton(text="Политика конфиденциальности", url="https://clck.ru/3GHACe")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_link(user):
    conn = get_db_connection()
    last_order = conn.execute('SELECT id FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user,)).fetchone()
    order_id = int(dict(last_order)['id']) + 100000
    last_cart = conn.execute('SELECT cart FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    last_cart = dict(last_cart)
    cart = int((last_cart['cart'].split('Итого:')[1]).split()[0])
    conn.close()
    url = f"https://payment.alfabank.ru/payment/rest/register.do?userName=r-club228829295-api&password=Gulnara18!!!&orderNumber={order_id}&amount={cart*100}&returnUrl=https://armada-wows-shop.ru/success"
    response = requests.get(url)
    k  = response.text
    print(k)
    await botik.send_message(user, text=f"Нажимая <b>Оплатить</b> Вы принимаете пользовательское соглашение", reply_markup=pay(url))




async def main():
    await dp.start_polling(botik)

if __name__ == "__main__":
    asyncio.run(main())
