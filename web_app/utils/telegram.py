import json
import requests
from typing import Optional, Dict, Any

def edit_telegram_message(
        bot_token: str,
        chat_id: str,
        message_id: int,
        new_text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "HTML"
) -> bool:
    """
    Редактирует существующее сообщение в Telegram.
    
    Args:
        bot_token: Токен бота
        chat_id: ID чата
        message_id: ID сообщения
        new_text: Новый текст сообщения
        reply_markup: Разметка клавиатуры
        parse_mode: Режим парсинга (HTML/Markdown)
    
    Returns:
        bool: True если успешно, False если произошла ошибка
    """
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": parse_mode
    }

    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, params=params).json()

    if response.get("ok"):
        return True
    else:
        print("Ошибка редактирования:", response)
        return False

def send_telegram(
        bot_token: str,
        chat_id: str,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Отправляет сообщение в Telegram.
    
    Args:
        text: Текст сообщения
        bot_token: Токен бота
        chat_id: ID чата
        reply_markup: Разметка клавиатуры
    
    Returns:
        bool: True если успешно, False если произошла ошибка
    """
    print(bot_token, chat_id, text)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, params=params).json()
    if response.get("ok"):
        return True
    else:
        print("Ошибка отправки:", response)
        return False 