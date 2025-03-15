import json
import logging
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import time
import asyncio
import aiohttp
import requests
from flask import request
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, FSInputFile
from aiogram.filters import Command
from aiogram.enums import ContentType
import bot.config as config
from bot.db import add_user, get_db_connection
from web_app.app import app
# Настройка пути к проекту
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

botik = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    print('wddsdw')
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

# Клавиатура для оплаты
def pay(link):
    buttons = [
        [InlineKeyboardButton(text="Оплатить", url=link)],
        [InlineKeyboardButton(text="Пользовательское соглашение", url="https://clck.ru/3GgzNq"),
         InlineKeyboardButton(text="Политика конфиденциальности", url="https://clck.ru/3GHACe")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Получение ссылки на оплату
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
    text = response.text
    print(type(text))
    print(text)
    try:
        k = json.loads(text)  # Ручное преобразование текста в JSON
    except json.JSONDecodeError as e:
        print("Ошибка при декодировании JSON:", e)
        return  # Прекращаем выполнение, если текст не является JSON

    if 'formUrl' in k:
        a = k['formUrl']
        message_obj = await botik.send_message(
            user,
            text="Нажимая «Оплатить» Вы принимаете положения Политики Конфиденциальности и Пользовательского Соглашения",
            reply_markup=pay(a)
        )
        conn = get_db_connection()
        conn.execute('UPDATE users SET message_id = ? WHERE telegram_id = ?', (message_obj.message_id, user))
        conn.commit()
        conn.close()
        await check(k['orderId'], user)
    else:
        print("Ключ 'formUrl' отсутствует в словаре k:", k)

# Получение текста заказа
async def order_text(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (user,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    else:
        return None

# Проверка статуса оплаты
async def check(orderId, user):
    url = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
    start_time = asyncio.get_event_loop().time()
    duration = 5 * 60  # 5 минут
    interval = 5  # Интервал проверки (5 секунд)
    glag = False
    session = None
    try:
        async with aiohttp.ClientSession() as session:
            while asyncio.get_event_loop().time() - start_time < duration:
                try:
                    async with session.get(url) as response:
                        text = await response.text()
                        data = json.loads(text)
                        if data['OrderStatus'] == 2:
                            glag = True
                            break
                except Exception as e:
                    print(f"Ошибка при запросе статуса заказа: {e}")
                await asyncio.sleep(interval)

        # После выполнения сессия будет автоматически закрыта
        conn = get_db_connection()
        if glag:
            await botik.edit_message_text(
                chat_id=user,
                message_id=conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0],
                text='Заказ успешно оплачен!'
            )
            conn.execute("DELETE FROM cart WHERE user_id = ?", (user,))
            conn.commit()
            data = await order_text(user)
            message = f"""
            Детали заказа:
            ———————————————
            🆔 ID заказа: {data['id']}
            👤 User ID: id <a href="tg://user?id={data['user_id']}">{data['user_id']}</a>
            🛒 Корзина: {data['cart']}
            🔑 OTP-код: {data['otp_code']}
            ———————————————
            Спасибо за ваш заказ! 😊
            """
            await botik.send_message(config.ADMIN_ID, message, parse_mode='HTML')
        else:
            await botik.edit_message_text(
                chat_id=user,
                message_id=conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0],
                text='Время на оплату истекло'
            )
            url2 = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
            async with aiohttp.ClientSession() as session2:
                await session2.get(url2)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if session:
            await session.close() 


# Запуск бота
# Обработчик сообщений из WebApp
@dp.message(lambda message: message.web_app_data)
async def web_app_handler(message: types.Message):
    data = message.web_app_data.data  # Получаем JSON-строку
    logging.info(f"Получены данные от WebApp: {data}")
    await message.answer(f"Данные получены: {data}")

# Основной обработчик вебхука
@app.route(config.WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    asyncio.run(dp.feed_update(botik, update))
    return {"ok": True}

# Функция для запуска бота
async def main():
    logging.info("Удаляем старый вебхук...")
    await botik.delete_webhook()

    logging.info(f"Устанавливаем новый вебхук: {config.WEBHOOK_URL}")
    await botik.set_webhook(url=config.WEBHOOK_URL)

    logging.info("Бот запущен через вебхук.")

# Запускаем бота
if __name__ == "__main__":
    asyncio.run(main())