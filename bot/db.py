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
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                price REAL NOT NULL,
                                image TEXT
                            );''')
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
