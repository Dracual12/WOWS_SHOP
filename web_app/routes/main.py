from flask import Blueprint, render_template, request, jsonify, current_app
from web_app import db
from ..utils.helpers import format_order_summary, order_text
from ..utils.telegram import send_telegram
from ..config import Config

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    current_app.logger.info('Открыта главная страница')
    return render_template('index.html')

@bp.route("/save-tg-id", methods=["POST"])
def save_tg_id():
    data = request.get_json()
    tg_id = data.get('tg_id')
    if tg_id:
        current_app.logger.info(f'Сохранен Telegram ID: {tg_id}')
        return jsonify({"status": "success"})
    current_app.logger.warning('Попытка сохранить пустой Telegram ID')
    return jsonify({"status": "error"})

@bp.route('/save-otp', methods=['POST'])
def save_otp():
    data = request.get_json()
    otp = data.get('otp')
    if otp:
        current_app.logger.info('Сохранен OTP код')
        return jsonify({"status": "success"})
    current_app.logger.warning('Попытка сохранить пустой OTP код')
    return jsonify({"status": "error"})

@bp.route('/save_tg_link', methods=['POST'])
def save_link():
    data = request.get_json()
    link = data.get('link')
    if link:
        current_app.logger.info(f'Сохранена ссылка: {link}')
        return jsonify({"status": "success"})
    current_app.logger.warning('Попытка сохранить пустую ссылку')
    return jsonify({"status": "error"})

@bp.route('/api/order/end', methods=['POST'])
def end_order():
    data = request.get_json()
    user = data.get('user')
    order_items = data.get('items', [])
    
    if user and order_items:
        current_app.logger.info(f'Оформлен заказ от пользователя: {user.get("name")}')
        order_summary = format_order_summary(order_items)
        order_details = order_text(user)
        message = f"{order_details}\n{order_summary}"
        
        if send_telegram(message, Config.BOT_TOKEN, Config.CHAT_ID):
            current_app.logger.info('Заказ успешно отправлен в Telegram')
            return jsonify({"status": "success"})
        else:
            current_app.logger.error('Ошибка отправки заказа в Telegram')
    else:
        current_app.logger.warning('Попытка оформить заказ с неполными данными')
    
    return jsonify({"status": "error"})

@bp.route('/api/order/latest', methods=['POST'])
def get_latest_order():
    current_app.logger.info('Запрос последнего заказа')
    return jsonify({"status": "success"})

@bp.route('/product/<int:product_id>')
def product_page(product_id):
    current_app.logger.info(f'Открыта страница товара: {product_id}')
    return render_template('product.html', product_id=product_id) 