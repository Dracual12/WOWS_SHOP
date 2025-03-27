import sqlite3
from web_app.config import Config

def update_database():
    # Подключаемся к базе данных
    conn = sqlite3.connect(Config.DATABASE['path'])
    cursor = conn.cursor()
    
    try:
        # Добавляем колонку order_index в таблицу sections
        cursor.execute("ALTER TABLE sections ADD COLUMN order_index INTEGER DEFAULT 0")
        
        # Добавляем колонку order_index в таблицу products
        cursor.execute("ALTER TABLE products ADD COLUMN order_index INTEGER DEFAULT 0")
        
        # Обновляем существующие записи
        cursor.execute("UPDATE sections SET order_index = id")
        cursor.execute("UPDATE products SET order_index = id")
        
        # Переименовываем колонку user_id в tg_id в таблице cart
        cursor.execute("ALTER TABLE cart RENAME COLUMN user_id TO tg_id")
        
        conn.commit()
        print("База данных успешно обновлена!")
        
    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_database() 