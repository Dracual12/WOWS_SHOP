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
            cursor.execute("SELECT * FROM products ORDER BY order_index")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_sections(self) -> List[Dict[str, Any]]:
        """Получает список всех разделов."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sections ORDER BY order_index")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_cart(self, tg_id: int) -> List[Dict[str, Any]]:
        """Получает содержимое корзины пользователя."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.product_id, c.tg_id, c.quantity, p.name, p.price 
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
                # Сначала проверяем, существует ли запись
                cursor.execute("""
                    SELECT quantity FROM cart 
                    WHERE product_id = ? AND tg_id = ?
                """, (product_id, tg_id))
                existing = cursor.fetchone()
                
                if existing:
                    # Если запись существует, обновляем количество
                    new_quantity = existing[0] + quantity
                    cursor.execute("""
                        UPDATE cart 
                        SET quantity = ? 
                        WHERE product_id = ? AND tg_id = ?
                    """, (new_quantity, product_id, tg_id))
                else:
                    # Если записи нет, создаем новую
                    cursor.execute("""
                        INSERT INTO cart (product_id, tg_id, quantity)
                        VALUES (?, ?, ?)
                    """, (product_id, tg_id, quantity))
                
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
                print(f"Попытка обновить количество: tg_id={tg_id}, product_id={product_id}, quantity={quantity}")
                
                # Проверяем все записи в корзине для этого пользователя
                cursor.execute("""
                    SELECT * FROM cart 
                    WHERE tg_id = ?
                """, (tg_id,))
                all_items = cursor.fetchall()
                print(f"Все товары в корзине пользователя {tg_id}: {all_items}")
                
                # Проверяем, существует ли запись
                cursor.execute("""
                    SELECT quantity FROM cart 
                    WHERE product_id = ? AND tg_id = ?
                """, (product_id, tg_id))
                existing = cursor.fetchone()
                print(f"Существующая запись: {existing}")
                
                if existing:
                    print("Запись найдена, обновляем количество")
                    cursor.execute("""
                        UPDATE cart 
                        SET quantity = ? 
                        WHERE product_id = ? AND tg_id = ?
                    """, (quantity, product_id, tg_id))
                    conn.commit()
                    print("Количество успешно обновлено")
                    return True
                else:
                    print("Запись не найдена")
                    return False
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
                    WHERE product_id = ? AND tg_id = ?
                """, (product_id, tg_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка удаления из корзины: {e}")
                return False

    def update_section_order(self, section_id: int, new_order: int) -> bool:
        """Обновляет порядок секции."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE sections 
                    SET order_index = ? 
                    WHERE id = ?
                """, (new_order, section_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка обновления порядка секции: {e}")
                return False

    def update_product_order(self, product_id: int, new_order: int) -> bool:
        """Обновляет порядок товара."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE products 
                    SET order_index = ? 
                    WHERE id = ?
                """, (new_order, product_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка обновления порядка товара: {e}")
                return False

    def reorder_sections(self, section_ids: List[int]) -> bool:
        """Обновляет порядок всех секций."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for order, section_id in enumerate(section_ids):
                    cursor.execute("""
                        UPDATE sections 
                        SET order_index = ? 
                        WHERE id = ?
                    """, (order, section_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка обновления порядка секций: {e}")
                return False

    def reorder_products(self, product_ids: List[int]) -> bool:
        """Обновляет порядок всех товаров."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for order, product_id in enumerate(product_ids):
                    cursor.execute("""
                        UPDATE products 
                        SET order_index = ? 
                        WHERE id = ?
                    """, (order, product_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Ошибка обновления порядка товаров: {e}")
                return False

    def add_product(self, name: str, description: str, price: float, section_id: int, image_path: str = None, order_index: int = 0, is_active: bool = True) -> bool:
        """Добавляет новый товар в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (name, description, price, section_id, image_path, order_index, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, price, section_id, image_path, order_index, is_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")
            return False 