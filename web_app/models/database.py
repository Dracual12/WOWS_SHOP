import sqlite3
from typing import List, Dict, Any, Optional
import os

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Создает необходимые таблицы, если они не существуют."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создаем таблицу sections
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Создаем таблицу products
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    image TEXT,
                    section TEXT,
                    review_link TEXT,
                    order_index INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Проверяем существующие столбцы в таблице products
            cursor.execute("PRAGMA table_info(products)")
            columns = [column[1] for column in cursor.fetchall()]
            print("Существующие столбцы в таблице products:", columns)
            
            # Добавляем отсутствующие столбцы
            if 'order_index' not in columns:
                cursor.execute('ALTER TABLE products ADD COLUMN order_index INTEGER DEFAULT 0')
            if 'is_active' not in columns:
                cursor.execute('ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1')
            if 'review_link' not in columns:
                cursor.execute('ALTER TABLE products ADD COLUMN review_link TEXT')
            
            # Создаем таблицу cart
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    tg_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    UNIQUE(product_id, tg_id)
                )
            ''')
            
            # Создаем таблицу orders
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицу order_items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Создает и возвращает соединение с базой данных."""
        return sqlite3.connect(self.db_path)

    def get_products(self) -> List[Dict]:
        """Получает список всех товаров"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, price, section, image, order_index, is_active, review_link
                    FROM products
                    WHERE is_active = 1
                    ORDER BY order_index
                ''')
                columns = [description[0] for description in cursor.description]
                products = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print("Полученные товары:", products)  # Добавляем отладочный вывод
                return products
        except Exception as e:
            print(f"Ошибка при получении списка товаров: {e}")
            return []

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

    def update_cart_item(self, tg_id: int, product_id: int, quantity: int) -> bool:
        """Обновляет количество товара в корзине"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cart (tg_id, product_id, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(tg_id, product_id) 
                    DO UPDATE SET quantity = ?
                """, (tg_id, product_id, quantity, quantity))
                return True
        except Exception as e:
            print(f"Ошибка при обновлении товара в корзине: {e}")
            return False

    def remove_from_cart(self, tg_id: int, product_id: int) -> bool:
        """Удаляет товар из корзины"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM cart 
                    WHERE tg_id = ? AND product_id = ?
                """, (tg_id, product_id))
                return True
        except Exception as e:
            print(f"Ошибка при удалении товара из корзины: {e}")
            return False

    def get_cart_items(self, tg_id: int) -> List[Dict]:
        """Получает все товары в корзине пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.name, p.price, c.quantity
                    FROM cart c
                    JOIN products p ON c.product_id = p.id
                    WHERE c.tg_id = ?
                """, (tg_id,))
                items = cursor.fetchall()
                
                return [{
                    'product_id': item[0],
                    'name': item[1],
                    'price': item[2],
                    'quantity': item[3]
                } for item in items]
        except Exception as e:
            print(f"Ошибка при получении товаров из корзины: {e}")
            return []

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

    def add_product(self, name: str, description: str, price: float, section_id: int, image_path: str = None, order_index: int = 0, is_active: bool = True, review_link: str = None) -> bool:
        """Добавляет новый товар в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Получаем название секции по ID
                cursor.execute('SELECT name FROM sections WHERE id = ?', (section_id,))
                section_name = cursor.fetchone()[0]
                
                print(f"Добавление товара: name={name}, section={section_name}, image_path={image_path}")  # Отладочный вывод
                cursor.execute('''
                    INSERT INTO products (name, description, price, section, image, order_index, is_active, review_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, price, section_name, image_path, order_index, is_active, review_link))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")
            return False

    def update_product(self, product_id: int, name: str, description: str, price: float, section_id: int, image_path: str = None, order_index: int = 0, is_active: bool = True, review_links: str = None) -> bool:
        """Обновляет товар в базе данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Получаем название секции по ID
                cursor.execute('SELECT name FROM sections WHERE id = ?', (section_id,))
                section_name = cursor.fetchone()[0]
                
                print(f"Обновление товара: id={product_id}, name={name}, section={section_name}, image_path={image_path}")  # Отладочный вывод
                cursor.execute('''
                    UPDATE products 
                    SET name = ?, description = ?, price = ?, section = ?, image = ?, order_index = ?, is_active = ?, review_link = ?
                    WHERE id = ?
                ''', (name, description, price, section_name, image_path, order_index, is_active, review_links, product_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при обновлении товара: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Удаляет товар из базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Сначала получаем информацию о товаре, чтобы удалить его изображение
                cursor.execute('SELECT image FROM products WHERE id = ?', (product_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    image_path = result[0]
                    full_path = os.path.join(os.path.dirname(self.db_path), '..', 'web_app', image_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
                
                # Удаляем товар из базы данных
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при удалении товара: {e}")
            return False

    def add_section(self, name, order_index=0, is_active=True):
        """Добавляет новый раздел"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sections (name, order_index, is_active)
                VALUES (?, ?, ?)
            ''', (name, order_index, is_active))
            
            conn.commit()
            print(f"Раздел '{name}' успешно добавлен")
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении раздела: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def create_order(self, user_id: int, login: str, password: str, items: List[Dict], total_price: float) -> Optional[int]:
        """Создает новый заказ"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Создаем заказ
                cursor.execute('''
                    INSERT INTO orders (user_id, login, password, total_price, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, login, password, total_price, 'new'))
                
                order_id = cursor.lastrowid
                
                # Добавляем товары заказа
                for item in items:
                    cursor.execute('''
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    ''', (order_id, item['product_id'], item['quantity'], item['price']))
                
                conn.commit()
                return order_id
                
        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")
            return None
            
    def clear_cart(self, tg_id: int) -> bool:
        """Очищает корзину пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart WHERE tg_id = ?', (tg_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при очистке корзины: {e}")
            return False

    def init_db(self):
        """Инициализирует базу данных"""
        try:
            cursor = self.get_connection().cursor()
            
            # Создаем таблицу products
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    section TEXT NOT NULL,
                    image TEXT,
                    review_links TEXT,
                    order_index INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Создаем таблицу sections
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Создаем таблицу cart
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            self.connection.commit()
            print("База данных успешно инициализирована")
            return True
        except Exception as e:
            print(f"Ошибка при инициализации базы данных: {e}")
            return False 