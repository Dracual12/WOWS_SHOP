import os
import re
import sys
import asyncio
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    Message,
    FSInputFile,
)

import bot.config as config
from bot.db import (
    add_user,
    get_db_connection,
    add_column,
    block_user,
    unblock_user,
    is_blocked,
    get_all_users,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Гарантируем наличие нужных колонок в БД
try:
    add_column('users')
except Exception as e:
    logger.error(f"Не удалось проверить/добавить колонку username в таблицу users: {e}")

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class PushState(StatesGroup):
    waiting_for_message = State()
    waiting_for_photo = State()


def extract_telegram_id_from_link(text: str):
    """Извлекает telegram_id из ссылки типа https://t.me/username или t.me/username или @username"""
    if not text:
        return None

    patterns = [
        r't\.me/(\w+)',
        r'https?://t\.me/(\w+)',
        r'@(\w+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    if text.strip().isdigit():
        return int(text.strip())

    return None


async def get_user_id_from_username(username: str):
    """Получает telegram_id пользователя по username через БД или API"""
    conn = get_db_connection()
    try:
        user = conn.execute(
            'SELECT telegram_id FROM users WHERE username = ?',
            (username,),
        ).fetchone()
        if user:
            return user['telegram_id']
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя в БД: {e}")
    finally:
        conn.close()

    try:
        chat = await bot.get_chat(f"@{username}")
        return chat.id
    except Exception as e:
        logger.warning(f"Не удалось получить ID пользователя {username} через API: {e}")
        return None


class BlacklistMiddleware(BaseMiddleware):
    """Middleware для проверки прав и блэклиста (aiogram 3.x)"""

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            telegram_id = event.from_user.id

            if event.text:
                text_lower = event.text.lower().split()[0]
                is_admin_command = any(text_lower.startswith(cmd) for cmd in ('/block', '/unblock', '/push'))

                if is_admin_command and telegram_id != config.ADMIN_ID:
                    await event.answer("У вас нет прав для выполнения этой команды.")
                    return  # Прерываем обработку, не вызывая handler

            if is_blocked(telegram_id):
                return  # Прерываем обработку, не вызывая handler

        return await handler(event, data)


dp.message.middleware.register(BlacklistMiddleware())


@dp.message(Command("start"))
async def send_welcome(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    add_user(telegram_id, username)

    # Путь к файлу относительно директории bot/
    bot_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.join(bot_dir, "assets", "welcome.jpeg")
    
    if not os.path.exists(photo_path):
        logger.error(f"Файл фото не найден: {photo_path}")
        await message.answer(
            '⚡️<b>«Армада Голд» представляет первый большой проект - «Армада Голд Бот». Здесь Вы можете:</b>\n\n'
            '• Приобрести дублоны и другие наборы на аккаунт любого региона и платформы;\n'
            '• Просмотреть видеообзоры на разные корабли;\n'
            '• Оценить бои от участников нашего канала\n\n'
            '<b>Чтобы начать, нажмите «Открыть магазин»</b> 👇',
            reply_markup=main_menu(),
        )
        return
    
    photo = FSInputFile(photo_path)

    await message.answer_photo(
        photo=photo,
        caption=(
            '⚡️<b>«Армада Голд» представляет первый большой проект - «Армада Голд Бот». Здесь Вы можете:</b>\n\n'
            '• Приобрести дублоны и другие наборы на аккаунт любого региона и платформы;\n'
            '• Просмотреть видеообзоры на разные корабли;\n'
            '• Оценить бои от участников нашего канала\n\n'
            '<b>Чтобы начать, нажмите «Открыть магазин»</b> 👇'
        ),
        reply_markup=main_menu(),
    )


@dp.message(Command("block"))
async def block_command(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

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

    if isinstance(username_or_id, str):
        user_id = await get_user_id_from_username(username_or_id)
        if not user_id:
            await message.answer(f"Не удалось найти пользователя @{username_or_id}. Убедитесь, что пользователь начинал диалог с ботом.")
            return
    else:
        user_id = username_or_id

    if block_user(user_id):
        await message.answer(f"Пользователь (ID: {user_id}) успешно заблокирован.")
    else:
        await message.answer(f"Ошибка при блокировке пользователя (ID: {user_id}). Возможно, он уже в блэклисте.")


@dp.message(Command("unblock"))
async def unblock_command(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

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

    if isinstance(username_or_id, str):
        user_id = await get_user_id_from_username(username_or_id)
        if not user_id:
            await message.answer(f"Не удалось найти пользователя @{username_or_id}. Убедитесь, что пользователь начинал диалог с ботом.")
            return
    else:
        user_id = username_or_id

    if unblock_user(user_id):
        await message.answer(f"Пользователь (ID: {user_id}) успешно разблокирован.")
    else:
        await message.answer(f"Пользователь (ID: {user_id}) не найден в блэклисте.")


@dp.message(Command("push"))
async def push_command(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    await message.answer("Отправьте текст сообщения, которое нужно разослать всем пользователям:")
    await state.set_state(PushState.waiting_for_message)


@dp.message(StateFilter(PushState.waiting_for_message))
async def process_push_text(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await state.clear()
        return

    text = (message.text or message.caption or "").strip()
    if not text:
        await message.answer("Сообщение не должно быть пустым. Пожалуйста, отправьте текст.")
        return

    await state.update_data(text=text)
    await message.answer(
        "Теперь отправьте фото, которое нужно прикрепить к сообщению.\n"
        "Если фото не нужно – напишите «нет» или «skip»."
    )
    await state.set_state(PushState.waiting_for_photo)


@dp.message(StateFilter(PushState.waiting_for_photo))
async def process_push_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await state.clear()
        return

    data = await state.get_data()
    text = data.get("text", "")

    photo_id = message.photo[-1].file_id if message.photo else None
    if not photo_id and message.text and message.text.strip().lower() in ("нет", "no", "skip"):
        photo_id = None

    users = get_all_users()
    if not users:
        await message.answer("В базе данных нет пользователей для рассылки.")
        await state.clear()
        return

    success_count = 0
    fail_count = 0

    await message.answer(f"Начинаю рассылку сообщения {len(users)} пользователям...")

    for user_id in users:
        try:
            if is_blocked(user_id):
                continue

            keyboard = get_web_app_keyboard()

            if photo_id:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=text,
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=keyboard,
                )
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            fail_count += 1

    await message.answer(
        f"Рассылка завершена!\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибок: {fail_count}"
    )
    await state.clear()


def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))],
        [InlineKeyboardButton(text="\U0001F4DD Отзывы", url="https://t.me/armada_feedback")],
        [InlineKeyboardButton(text="\U0001F4E9 Задать вопрос", url="https://t.me/armada_support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_web_app_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Открыть Магазин", web_app=WebAppInfo(url=config.WEB_APP_URL))]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def main():
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error while running bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}")