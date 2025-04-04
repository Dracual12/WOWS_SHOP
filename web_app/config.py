import os
class Config:
    # Пути
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'bot', 'wows_db.db')
    #ADMIN_ID = 432771577
    ADMIN_ID = 1456241115
    # Конфигурация Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    BOT_TOKEN = "7574071837:AAFE0A2rW27YmxOi40AG68577fK3zluinu4"
    # Конфигурация базы данных
    DATABASE = {
        'path': DB_PATH
    }
    
    # Конфигурация Telegram
    CHAT_ID = os.environ.get('CHAT_ID')
    
    # Конфигурация Альфа-банка
    ALFABANK_TOKEN = os.environ.get('ALFABANK_TOKEN')
    
    # Настройки для загрузки файлов
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'bot', 'assets')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max-limit

    # Учетные данные администратора
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123' 