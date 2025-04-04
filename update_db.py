import sqlite3
import os
import sys

def update_database(db_path):
    """Обновляет структуру базы данных"""
    print(f"Обновление базы данных: {db_path}")
    
    # Проверяем существование файла базы данных
    if not os.path.exists(db_path):
        print(f"Ошибка: Файл базы данных {db_path} не найден")
        return False
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование колонки is_active в таблице sections
        cursor.execute("PRAGMA table_info(sections)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Добавляем колонку is_active, если она отсутствует
        if 'is_active' not in columns:
            print("Добавление колонки is_active в таблицу sections...")
            cursor.execute('ALTER TABLE sections ADD COLUMN is_active BOOLEAN DEFAULT 1')
            print("Колонка is_active успешно добавлена")
        else:
            print("Колонка is_active уже существует в таблице sections")
        
        # Проверяем существование колонки is_active в таблице products
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Добавляем колонку is_active, если она отсутствует
        if 'is_active' not in columns:
            print("Добавление колонки is_active в таблицу products...")
            cursor.execute('ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT 1')
            print("Колонка is_active успешно добавлена")
        else:
            print("Колонка is_active уже существует в таблице products")
        
        # Сохраняем изменения
        conn.commit()
        print("База данных успешно обновлена")
        return True
    
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении базы данных: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Путь к базе данных
    db_path = "web_app/database.db"
    
    # Если указан аргумент командной строки, используем его как путь к базе данных
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    # Обновляем базу данных
    update_database(db_path) 