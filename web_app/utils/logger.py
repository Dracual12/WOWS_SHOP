import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Создаем директорию для логов, если она не существует
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Настраиваем формат логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Настраиваем файл для всех логов
    app_log = os.path.join(log_dir, 'app.log')
    app_handler = RotatingFileHandler(app_log, maxBytes=10*1024*1024, backupCount=5)
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)
    
    # Настраиваем файл для ошибок
    error_log = os.path.join(log_dir, 'error.log')
    error_handler = RotatingFileHandler(error_log, maxBytes=10*1024*1024, backupCount=5)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Добавляем вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger 