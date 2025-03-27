from flask import Flask
from flask_cors import CORS
from .utils.logger import setup_logger
from .config import Config
from .models.database import Database
import os

# Создаем экземпляр базы данных
db = Database(Config.DATABASE['path'])

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    CORS(app)
    
    # Регистрация конфигурации
    app.config.from_object(Config)
    
    # Настройка логирования
    setup_logger(app)
    
    # Регистрация блюпринтов
    from .routes import main, admin, api
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)
    
    app.logger.info('Application initialized successfully')
    return app 