from typing import List, Dict, Any

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

def order_text(user: Dict[str, Any]) -> str:
    """
    Формирует текст заказа.
    
    Args:
        user: Информация о пользователе
    
    Returns:
        str: Текст заказа
    """
    return f"Заказ от {user['name']}\nТелефон: {user['phone']}\nEmail: {user['email']}" 