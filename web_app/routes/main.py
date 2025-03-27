from flask import Blueprint, render_template, request, jsonify
from ..models.database import db
from ..utils.helpers import format_order_summary, order_text
from ..utils.telegram import send_telegram
from ..config import Config

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route("/save-tg-id", methods=["POST"])
def save_tg_id():
    data = request.get_json()
    tg_id = data.get('tg_id')
    if tg_id:
        # Здесь можно добавить сохранение tg_id в базу данных
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/save-otp', methods=['POST'])
def save_otp():
    data = request.get_json()
    otp = data.get('otp')
    if otp:
        # Здесь можно добавить сохранение OTP в базу данных
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/save_tg_link', methods=['POST'])
def save_link():
    data = request.get_json()
    link = data.get('link')
    if link:
        # Здесь можно добавить сохранение ссылки в базу данных
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/api/order/end', methods=['POST'])
def end_order():
    data = request.get_json()
    user = data.get('user')
    order_items = data.get('items', [])
    
    if user and order_items:
        order_summary = format_order_summary(order_items)
        order_details = order_text(user)
        message = f"{order_details}\n{order_summary}"
        
        if send_telegram(message, Config.BOT_TOKEN, Config.CHAT_ID):
            return jsonify({"status": "success"})
    
    return jsonify({"status": "error"})

@bp.route('/api/order/latest', methods=['POST'])
def get_latest_order():
    # Здесь можно добавить логику получения последнего заказа
    return jsonify({"status": "success"})

@bp.route('/product/<int:product_id>')
def product_page(product_id):
    return render_template('product.html', product_id=product_id) 