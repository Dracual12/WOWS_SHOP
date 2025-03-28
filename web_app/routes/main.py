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

@bp.route('/api/sections')
def get_sections():
    current_app.logger.info('Запрос списка секций и товаров')
    try:
        sections = db.get_sections()
        products = db.get_products()
        
        current_app.logger.info(f'Получено разделов: {len(sections)}')
        current_app.logger.info(f'Получено товаров: {len(products)}')
        current_app.logger.info(f'Секции: {sections}')
        current_app.logger.info(f'Товары: {products}')
        
        # Сортируем секции по order_index
        sorted_sections = sorted(sections, key=lambda x: x['order_index'])
        
        # Группируем товары по разделам
        sections_with_products = []
        for section in sorted_sections:
            section_products = [p for p in products if p.get('section') == section['name']]
            current_app.logger.info(f'Товары для раздела {section["name"]}: {section_products}')
            sections_with_products.append({
                'id': section['id'],
                'section_name': section['name'],
                'products': section_products
            })
        
        current_app.logger.info(f'Итоговый результат: {sections_with_products}')
        return jsonify(sections_with_products)
    except Exception as e:
        current_app.logger.error(f'Ошибка при получении разделов: {str(e)}')
        return jsonify({"status": "error", "message": str(e)}), 500

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
    try:
        # Получаем все товары
        products = db.get_products()
        # Находим нужный товар
        product = next((p for p in products if p['id'] == product_id), None)
        
        if product:
            current_app.logger.info(f'Товар найден: {product}')
            return render_template('product.html', product=product)
        else:
            current_app.logger.error(f'Товар с ID {product_id} не найден')
            return render_template('product.html', product=None)
    except Exception as e:
        current_app.logger.error(f'Ошибка при получении товара: {str(e)}')
        return render_template('product.html', product=None)

@bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    current_app.logger.info('Получен запрос на добавление товара в корзину')
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        tg_id = data.get('tg_id')
        quantity = data.get('quantity', 1)
        
        if not product_id or not tg_id:
            current_app.logger.error('Отсутствуют обязательные параметры')
            return jsonify({"status": "error", "message": "Отсутствуют обязательные параметры"}), 400
        
        current_app.logger.info(f'Добавление товара {product_id} в корзину пользователя {tg_id}')
        
        if db.add_to_cart(tg_id, product_id, quantity):
            current_app.logger.info('Товар успешно добавлен в корзину')
            return jsonify({"status": "success"})
        else:
            current_app.logger.error('Ошибка при добавлении товара в корзину')
            return jsonify({"status": "error", "message": "Ошибка при добавлении товара в корзину"}), 500
            
    except Exception as e:
        current_app.logger.error(f'Ошибка при добавлении товара в корзину: {str(e)}')
        return jsonify({"status": "error", "message": str(e)}), 500 