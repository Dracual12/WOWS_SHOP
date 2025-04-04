from typing import List, Dict, Any
from web_app import db

def format_order_summary(order_items: List[Dict[str, Any]]) -> str:
    """
    Форматирует итоговую стоимость заказа.
    
    Args:
        order_items: Список товаров в заказе
    
    Returns:
        str: Отформатированная строка с итоговой стоимостью
    """
    total = sum(item['price'] * item['quantity'] for item in order_items)
    return f"Итоговая стоимость: {total}₽"

def order_text(user_id: int) -> Dict[str, Any]:
    """
    Формирует текст заказа на основе корзины пользователя.
    
    Args:
        user_id: ID пользователя в Telegram
    
    Returns:
        Dict[str, Any]: Словарь с информацией о заказе, включая:
            - id: ID заказа
            - user_id: ID пользователя
            - cart: Текст корзины с товарами и их количеством
            - total: Общая стоимость заказа
    """
    # Получаем товары из корзины пользователя
    cart_items = db.get_cart_items(user_id)
    
    # Формируем текст корзины
    cart_text = ""
    total = 0
    
    for item in cart_items:
        item_total = item['price'] * item['quantity']
        total += item_total
        cart_text += f"• {item['name']} x{item['quantity']} = {item_total}₽\n"
    
    # Добавляем итоговую стоимость
    cart_text += f"\nИтого: {total}₽"
    
    # Возвращаем словарь с информацией о заказе
    return {
        "id": None,  # ID заказа будет установлен позже
        "user_id": user_id,
        "cart": cart_text,
        "total": total
    } 