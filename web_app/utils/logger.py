import os
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app

def setup_logger(app):
    """
    Настраивает систему логирования для приложения.
    
    Args:
        app: Flask приложение
    """
    # Создаем директорию для логов, если её нет
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Настраиваем формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настраиваем файловый обработчик
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,  # 10KB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Настраиваем обработчик для ошибок
    error_file_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10240,
        backupCount=10
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # Настраиваем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Добавляем обработчики к логгеру приложения
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Отключаем логирование от Werkzeug (по умолчанию)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Логируем информацию о запуске приложения
    app.logger.info('Логирование настроено') 