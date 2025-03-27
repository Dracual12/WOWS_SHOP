import sqlite3
from typing import List, Dict, Any, Optional
import os

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Создает и возвращает соединение с базой данных."""
        return sqlite3.connect(self.db_path)

    def get_products(self) -> List[Dict[str, Any]]:
        """Получает список всех товаров."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_sections(self) -> List[Dict[str, Any]]:
        """Получает список всех разделов."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sections")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_cart(self, tg_id: int) -> List[Dict[str, Any]]:
        """Получает содержимое корзины пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, p.name, p.price 
                FROM cart c 
                JOIN products p ON c.product_id = p.id 
                WHERE c.tg_id = ?
            """, (tg_id,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_to_cart(self, tg_id: int, product_id: int, quantity: int = 1) -> bool:
        """Добавляет товар в корзину пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO cart (tg_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(tg_id, product_id) 
                    DO UPDATE SET quantity = quantity + ?
                """, (tg_id, product_id, quantity, quantity))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка добавления в корзину: {e}")
                return False

    def update_cart_quantity(self, tg_id: int, product_id: int, quantity: int) -> bool:
        """Обновляет количество товара в корзине."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE cart 
                    SET quantity = ? 
                    WHERE tg_id = ? AND product_id = ?
                """, (quantity, tg_id, product_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка обновления корзины: {e}")
                return False

    def delete_cart_item(self, tg_id: int, product_id: int) -> bool:
        """Удаляет товар из корзины."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    DELETE FROM cart 
                    WHERE tg_id = ? AND product_id = ?
                """, (tg_id, product_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка удаления из корзины: {e}")
                return False 