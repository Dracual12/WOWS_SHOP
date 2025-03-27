import sqlite3
import os
from os.path import curdir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "wows_db.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor = conn.cursor()
    
    # Создаем таблицу sections с полем order
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL DEFAULT 0
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT,
        section_id INTEGER,
        order_index INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (section_id) REFERENCES sections (id)
    );
    ''')
    
    conn.commit()
    conn.close()

def add_user(telegram_id, username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
    if not user:
        conn.execute(
            'INSERT INTO users (telegram_id, username) VALUES (?, ?)',
            (telegram_id, username)
        )
        conn.commit()

    conn.close()

def add_order_id(order_id, user_id):
    conn = get_db_connection()
    orders_history = conn.execute("SELECT orders_historu FROM users WHERE user_id = ?", (user_id,)).fetchone()
    print(orders_history)
    if orders_history != None:
        orders_history += f', {order_id}'
    else:
        orders_history += order_id
    conn.execute('UPDATE users SET orders_history = ? WHERE user_id = ?', (orders_history, user_id))


def get_user(telegram_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
    conn.close()
    return user


def add_column(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        if 'username' not in columns:
            # Добавляем новый столбец
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN username TEXT")
            conn.commit()
            print(f"Столбец 'username' успешно добавлен в таблицу '{table_name}'")
        else:
            print(f"Столбец 'username' уже существует в таблице '{table_name}'")

    except sqlite3.Error as e:
        print(f"Ошибка при добавлении столбца: {e}")
    finally:
        if conn:
            conn.close()

def update_section_order(section_id, new_order):
    """Обновляет порядок секции"""
    conn = get_db_connection()
    try:
        conn.execute('UPDATE sections SET order_index = ? WHERE id = ?', (new_order, section_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении порядка секции: {e}")
        return False
    finally:
        conn.close()

def update_product_order(product_id, new_order):
    """Обновляет порядок товара"""
    conn = get_db_connection()
    try:
        conn.execute('UPDATE products SET order_index = ? WHERE id = ?', (new_order, product_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении порядка товара: {e}")
        return False
    finally:
        conn.close()

def get_sections_ordered():
    """Получает все секции, отсортированные по order_index"""
    conn = get_db_connection()
    try:
        sections = conn.execute('SELECT * FROM sections ORDER BY order_index').fetchall()
        return sections
    finally:
        conn.close()

def get_products_ordered(section_id=None):
    """Получает все товары, отсортированные по order_index"""
    conn = get_db_connection()
    try:
        if section_id:
            products = conn.execute('SELECT * FROM products WHERE section_id = ? ORDER BY order_index', (section_id,)).fetchall()
        else:
            products = conn.execute('SELECT * FROM products ORDER BY order_index').fetchall()
        return products
    finally:
        conn.close()

def reorder_sections(section_ids):
    """Обновляет порядок всех секций"""
    conn = get_db_connection()
    try:
        for order, section_id in enumerate(section_ids):
            conn.execute('UPDATE sections SET order_index = ? WHERE id = ?', (order, section_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении порядка секций: {e}")
        return False
    finally:
        conn.close()

def reorder_products(product_ids):
    """Обновляет порядок всех товаров"""
    conn = get_db_connection()
    try:
        for order, product_id in enumerate(product_ids):
            conn.execute('UPDATE products SET order_index = ? WHERE id = ?', (order, product_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении порядка товаров: {e}")
        return False
    finally:
        conn.close()
