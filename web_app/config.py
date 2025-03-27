import os

# Пути
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'bot', 'wows_db.db')

# Конфигурация Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Конфигурация Telegram
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Конфигурация базы данных
DATABASE = {
    'path': DB_PATH
} 