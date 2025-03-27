from flask import Blueprint, request, jsonify
from ..models.database import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    tg_id = data.get('tg_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if tg_id and product_id:
        if db.add_to_cart(tg_id, product_id, quantity):
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/cart', methods=['GET'])
def get_cart():
    tg_id = request.args.get('tg_id')
    if tg_id:
        cart_items = db.get_cart(int(tg_id))
        return jsonify({"status": "success", "items": cart_items})
    return jsonify({"status": "error"})

@bp.route('/cart/<int:product_id>', methods=['PUT'])
def update_cart_quantity(product_id):
    data = request.get_json()
    tg_id = data.get('tg_id')
    quantity = data.get('quantity')
    
    if tg_id and quantity:
        if db.update_cart_quantity(tg_id, product_id, quantity):
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/cart/<int:tg_id>/<int:product_id>', methods=['DELETE'])
def delete_cart_item(tg_id, product_id):
    if db.delete_cart_item(tg_id, product_id):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@bp.route('/products', methods=['GET'])
def get_products():
    products = db.get_products()
    return jsonify({"status": "success", "products": products})

@bp.route('/sections', methods=['GET'])
def get_sections():
    sections = db.get_sections()
    return jsonify({"status": "success", "sections": sections})

@bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    # Здесь можно добавить логику оформления заказа
    return jsonify({"status": "success"}) 