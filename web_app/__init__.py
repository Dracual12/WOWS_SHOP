from flask import Flask
from .config import Config
from .models.database import Database

db = Database(Config.DATABASE['path'])

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Регистрация маршрутов
    from .routes import main, api, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(admin.bp)

    return app 