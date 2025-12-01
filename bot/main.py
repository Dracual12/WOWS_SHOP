import json
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from typing import Callable, Dict, Any, Awaitable
import bot.config as config
from bot.db import add_user, get_db_connection, add_column, block_user, unblock_user, is_blocked, get_all_users
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Гарантируем наличие нужных колонок в БД
try:
    add_column('users')
except Exception as e:
    logger.error(f"Не удалось проверить/добавить колонку username в таблицу users: {e}")

# Инициализация бота и диспетчера
botik = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(botik, storage=storage)

# Состояния для FSM
class PushState(StatesGroup):
    waiting_for_message = State()
    waiting_for_photo = State()

# Функция для извлечения telegram_id из ссылки
def extract_telegram_id_from_link(text):
    """Извлекает telegram_id из ссылки типа https://t.me/username или t.me/username или @username"""
    if not text:
        return None
    
    # Паттерны для разных форматов ссылок
    patterns = [
        r't\.me/(\w+)',  # t.me/username
        r'https?://t\.me/(\w+)',  # https://t.me/username
        r'@(\w+)',  # @username
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            username = match.group(1)
            # Пытаемся получить user по username через API
            # Но для этого нужен реальный запрос к API, поэтому вернем username
            # В реальности нужно будет использовать get_chat для получения ID
            return username
    
    # Если это просто число (прямой ID)
    if text.strip().isdigit():
        return int(text.strip())
    
    return None

async def get_user_id_from_username(username):
    """Получает telegram_id пользователя по username через API или БД"""
    # Сначала пробуем найти в БД
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT telegram_id FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            return user['telegram_id']
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя в БД: {e}")
    finally:
        conn.close()
    
    # Если не нашли в БД, пробуем через API
    try:
        chat = await botik.get_chat(f"@{username}")
        return chat.id
    except Exception as e:
        # Это нормальная ситуация, если пользователь не писал боту или username некорректен
        logger.warning(f"Не удалось получить ID пользователя {username} через API: {e}")
        return None

class BlacklistMiddleware(BaseMiddleware):
    """Middleware для проверки блэклиста (aiogram 2.x)"""

    async def on_process_message(self, message: types.Message, data: dict):
        telegram_id = message.from_user.id

        # Проверяем, является ли сообщение командой /block, /unblock или /push
        if message.text:
            text_lower = message.text.lower().split()[0]
            is_admin_command = any(text_lower.startswith(cmd) for cmd in ('/block', '/unblock', '/push'))

            if is_admin_command:
                # Команды /block, /unblock, /push доступны только админу
                if telegram_id != config.ADMIN_ID:
                    await message.answer("У вас нет прав для выполнения этой команды.")
                    # Прерываем дальнейшую обработку
                    raise CancelHandler()
                # Админ может выполнять команды, даже если он в блэклисте
                return

        # Проверяем блэклист для всех остальных сообщений
        if is_blocked(telegram_id):
            # Просто игнорируем сообщение, не отвечаем
            raise CancelHandler()


# Регистрируем middleware
dp.middleware.setup(BlacklistMiddleware())

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    username = (message.from_user.username)
    add_user(telegram_id, username)
    photo = InputFile(f"{os.getcwd()}/assets/welcome.jpeg")
    await botik.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=(
            f'⚡️<b>«Армада Голд» представляет первый большой проект - «Армада Голд Бот». Здесь Вы можете:</b>\n\n'
            f'• Приобрести дублоны и другие наборы на аккаунт любого региона и платформы;\n'
            f'• Просмотреть видеообзоры на разные корабли;\n'
            f'• Оценить бои от участников нашего канала\n\n'

            f'<b>Чтобы начать, нажмите «Открыть магазин»</b> 👇'
        ),
        reply_markup=main_menu(),
        parse_mode='HTML'
    )

# Команда /block
@dp.message_handler(commands=['block'])
async def block_command(message: types.Message):
    """Обработчик команды /block"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # Проверяем, есть ли ссылка в сообщении
    command_text = message.text or ""
    parts = command_text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer("Использование: /block <ссылка на пользователя>\nПример: /block https://t.me/username или /block @username")
        return
    
    link = parts[1]
    username_or_id = extract_telegram_id_from_link(link)
    
    if not username_or_id:
        await message.answer("Не удалось извлечь информацию о пользователе из ссылки. Попробуйте отправить ссылку в формате: https://t.me/username или @username")
        return
    
    # Если это username, пытаемся получить ID
    if isinstance(username_or_id, str):
        user_id = await get_user_id_from_username(username_or_id)
        if not user_id:
            await message.answer(f"Не удалось найти пользователя @{username_or_id}. Убедитесь, что пользователь начинал диалог с ботом.")
            return
    else:
        user_id = username_or_id
    
    # Блокируем пользователя
    if block_user(user_id):
        await message.answer(f"Пользователь (ID: {user_id}) успешно заблокирован.")
    else:
        await message.answer(f"Ошибка при блокировке пользователя (ID: {user_id}). Возможно, он уже в блэклисте.")

# Команда /unblock
@dp.message_handler(commands=['unblock'])
async def unblock_command(message: types.Message):
    """Обработчик команды /unblock"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # Проверяем, есть ли ссылка в сообщении
    command_text = message.text or ""
    parts = command_text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer("Использование: /unblock <ссылка на пользователя>\nПример: /unblock https://t.me/username или /unblock @username")
        return
    
    link = parts[1]
    username_or_id = extract_telegram_id_from_link(link)
    
    if not username_or_id:
        await message.answer("Не удалось извлечь информацию о пользователе из ссылки. Попробуйте отправить ссылку в формате: https://t.me/username или @username")
        return
    
    # Если это username, пытаемся получить ID
    if isinstance(username_or_id, str):
        user_id = await get_user_id_from_username(username_or_id)
        if not user_id:
            await message.answer(f"Не удалось найти пользователя @{username_or_id}. Убедитесь, что пользователь начинал диалог с ботом.")
            return
    else:
        user_id = username_or_id
    
    # Разблокируем пользователя
    if unblock_user(user_id):
        await message.answer(f"Пользователь (ID: {user_id}) успешно разблокирован.")
    else:
        await message.answer(f"Пользователь (ID: {user_id}) не найден в блэклисте.")

# Команда /push
@dp.message_handler(commands=['push'])
async def push_command(message: types.Message, state: FSMContext):
    """Обработчик команды /push"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    await message.answer("Отправьте текст сообщения, которое нужно разослать всем пользователям:")
    await state.set_state(PushState.waiting_for_message)

@dp.message_handler(state=PushState.waiting_for_message)
async def process_push_text(message: types.Message, state: FSMContext):
    """Получаем текст для рассылки и переходим к этапу с фото"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await state.finish()
        return

    text = message.text or message.caption or ""
    if not text.strip():
        await message.answer("Сообщение не должно быть пустым. Пожалуйста, отправьте текст.")
        return

    await state.update_data(text=text)
    await message.answer(
        "Теперь отправьте фото, которое нужно прикрепить к сообщению.\n"
        "Если фото не нужно – напишите «нет» или «skip»."
    )
    await state.set_state(PushState.waiting_for_photo)


@dp.message_handler(state=PushState.waiting_for_photo, content_types=types.ContentTypes.ANY)
async def process_push_broadcast(message: types.Message, state: FSMContext):
    """Обработчик этапа с фото и запуск рассылки"""
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await state.finish()
        return

    data = await state.get_data()
    text = data.get("text", "")

    photo_id = None
    # Если админ прислал фото – используем его
    if message.photo:
        photo_id = message.photo[-1].file_id
    else:
        # Проверяем, хочет ли админ пропустить фото
        if message.text:
            if message.text.strip().lower() in ("нет", "no", "skip"):
                photo_id = None
            else:
                # Админ отправил текст вместо фото, но не "нет" — считаем, что это всё равно текст сообщения
                # и запускаем рассылку только с текстом.
                photo_id = None

    # Получаем всех пользователей
    users = get_all_users()
    
    if not users:
        await message.answer("В базе данных нет пользователей для рассылки.")
        await state.finish()
        return
    
    # Отправляем сообщение всем пользователям
    success_count = 0
    fail_count = 0
    
    await message.answer(f"Начинаю рассылку сообщения {len(users)} пользователям...")
    
    for user_id in users:
        try:
            # Пропускаем заблокированных пользователей
            if is_blocked(user_id):
                continue
            
            # Создаем клавиатуру с кнопкой web_app
            keyboard = get_web_app_keyboard()
            
            # Отправляем сообщение
            # Всегда шлём в формате HTML
            parse_mode = 'HTML'

            if photo_id:
                # Фото с подписью
                await botik.send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=keyboard
                )
            else:
                # Обычное текстовое сообщение
                await botik.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=keyboard
                )
            success_count += 1
            # Небольшая задержка, чтобы не превысить лимиты API
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            fail_count += 1
    
    await message.answer(
        f"Рассылка завершена!\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибок: {fail_count}"
    )
    await state.finish()

# Главное меню
def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))],
        [InlineKeyboardButton(text="\U0001F4DD Отзывы", url="https://t.me/armada_feedback")],
        [InlineKeyboardButton(text="\U0001F4E9 Задать вопрос", url="https://t.me/armada_support")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура с кнопкой web_app для рассылки
def get_web_app_keyboard():
    """Создает клавиатуру с кнопкой для открытия web_app"""
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Запуск бота
async def main():
    try:
        logger.info("Starting bot...")
        await dp.start_polling()
    except Exception as e:
        logger.error(f"Error while starting bot: {e}")
        # Даем время на освобождение ресурсов
        await asyncio.sleep(5)
        # Пробуем перезапустить бота
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")