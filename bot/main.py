import sys
import os
import time
from pyexpat.errors import messages

from flask import request

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
    with open(f"{os.getcwd()}/bot/assets/welcome.jpeg", "rb") as image:
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
    order_id = int(dict(last_order)['id']) + 100060
    last_cart = conn.execute('SELECT cart FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    last_cart = dict(last_cart)
    cart = int((last_cart['cart'].split('Итого:')[1]).split()[0])
    conn.close()
    url = f"https://payment.alfabank.ru/payment/rest/register.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderNumber={order_id}&amount={cart}&returnUrl=https://t.me/armada_gold_bot"
    response = requests.get(url)

    k  = response.json()
    if 'formUrl' in k:
        a = k['formUrl']
        message_obj = await botik.send_message(user,
                                               text=f"Нажимая «Оплатить»  Вы принимаете положения Политики Конфиденциальности и Пользовательского Соглашения",
                                               reply_markup=pay(a))
        conn = get_db_connection()
        order_message_id = conn.execute('UPDATE users SET message_id = ? WHERE telegram_id = ?',
                                        (message_obj.message_id, user))
        conn.commit()
        conn.close()
        await check(k['orderId'], user)
    else:
        print("Ключ 'formUrl' отсутствует в словаре k:", k)
        # Обработайте ситуацию, когда ключа нет

async def order_text(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Выполняем SQL-запрос для получения последнего заказа
    cursor.execute("""
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY id DESC 
            LIMIT 1
        """, (user,))
    row = cursor.fetchone()  # Получаем первую запись

    conn.close()  # Закрываем соединение с базой данных

    if row:
        # Преобразуем строку в словарь
        return dict(row)
    else:
        return None


async def check(orderId, user):
    url = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
    start_time = time.time()
    duration = 5 * 60
    interval = 5
    glag = False
    while time.time() - start_time < duration:
        data = requests.get(url).json()
        if data['OrderStatus'] == 2:
            glag = True
            break
        time.sleep(interval)

    conn = get_db_connection()
    if glag:
        row = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (user,)).fetchone()
        if row:
            # Преобразуем в словарь
            row_dict = dict(row)
        await botik.edit_message_text(
            chat_id=user,  # ID чата (telegram_id пользователя)
            message_id=conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0],
            # ID сообщения
            text='Заказ успешно оплачен!'  # Текст сообщения (строка)
        )
        conn.execute("DELETE FROM cart WHERE user_id = ?", (user,))
        conn.commit()
        data = await order_text(user)
        print(data)
        message = f"""
        <b>Детали заказа:</b>
        ———————————————
        🆔 <b>ID заказа:</b> {data['id']}
        👤 <b>User ID:</b> {data['user_id']}
        🛒 <b>Корзина:</b> {data['cart']}
        🔑 <b>OTP-код:</b> {data['otp_code']}
        🔗 <b>Ссылка на Telegram:</b> <a href="{data['telegram_link']}">Перейти</a>
        ———————————————
        Спасибо за ваш заказ! 😊
        """
        await botik.send_message(config.ADMIN_ID, message)
    else:
        await botik.edit_message_text(user, conn.execute('SELECT message_id FROM users WHERE telegram_id = ?',
                                                         (user,)).fetchone()[0], 'Время на оплату истекло')
        url2 = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
        requests.get(url2)

async def main():
    await dp.start_polling(botik)

if __name__ == "__main__":
    asyncio.run(main())
