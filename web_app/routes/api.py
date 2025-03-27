from flask import Blueprint, request, jsonify, current_app
from web_app import db
from ..utils.helpers import format_order_summary, order_text
from ..utils.telegram import send_telegram
from ..config import Config

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    tg_id = data.get('tg_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if tg_id and product_id:
        current_app.logger.info(f'Добавление товара {product_id} в корзину пользователя {tg_id}')
        if db.add_to_cart(tg_id, product_id, quantity):
            current_app.logger.info('Товар успешно добавлен в корзину')
            return jsonify({"status": "success"})
        else:
            current_app.logger.error('Ошибка добавления товара в корзину')
    else:
        current_app.logger.warning('Попытка добавить товар в корзину с неполными данными')
    return jsonify({"status": "error"})

@bp.route('/cart', methods=['GET'])
def get_cart():
    tg_id = request.args.get('tg_id')
    if tg_id:
        current_app.logger.info(f'Запрос корзины пользователя {tg_id}')
        cart_items = db.get_cart(int(tg_id))
        return jsonify({"status": "success", "items": cart_items})
    current_app.logger.warning('Попытка получить корзину без указания tg_id')
    return jsonify({"status": "error"})

@bp.route('/cart/<int:product_id>', methods=['PUT'])
def update_cart_quantity(product_id):
    data = request.get_json()
    tg_id = data.get('tg_id')
    quantity = data.get('quantity')
    
    if tg_id and quantity:
        current_app.logger.info(f'Обновление количества товара {product_id} в корзине пользователя {tg_id}')
        if db.update_cart_quantity(tg_id, product_id, quantity):
            current_app.logger.info('Количество товара успешно обновлено')
            return jsonify({"status": "success"})
        else:
            current_app.logger.error('Ошибка обновления количества товара')
    else:
        current_app.logger.warning('Попытка обновить количество товара с неполными данными')
    return jsonify({"status": "error"})

@bp.route('/cart/<int:tg_id>/<int:product_id>', methods=['DELETE'])
def delete_cart_item(tg_id, product_id):
    current_app.logger.info(f'Удаление товара {product_id} из корзины пользователя {tg_id}')
    if db.delete_cart_item(tg_id, product_id):
        current_app.logger.info('Товар успешно удален из корзины')
        return jsonify({"status": "success"})
    current_app.logger.error('Ошибка удаления товара из корзины')
    return jsonify({"status": "error"})

@bp.route('/products', methods=['GET'])
def get_products():
    current_app.logger.info('Запрос списка всех товаров')
    products = db.get_products()
    return jsonify({"status": "success", "products": products})

@bp.route('/sections', methods=['GET'])
def get_sections():
    current_app.logger.info('Запрос списка всех разделов')
    sections = db.get_sections()
    return jsonify({"status": "success", "sections": sections})

@bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    current_app.logger.info('Запрос оформления заказа')
    # Здесь можно добавить логику оформления заказа
    return jsonify({"status": "success"}) 