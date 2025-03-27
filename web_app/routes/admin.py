from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from ..models.database import db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'])
def admin_panel():
    current_app.logger.info('Открыта панель администратора')
    return render_template('admin/index.html')

@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = request.form
        current_app.logger.info('Попытка добавления нового товара')
        # Здесь можно добавить логику добавления товара
        current_app.logger.info('Товар успешно добавлен')
        return redirect(url_for('admin.admin_panel'))
    current_app.logger.info('Открыта страница добавления товара')
    return render_template('admin/add_product.html')

@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        data = request.form
        current_app.logger.info(f'Попытка редактирования товара {product_id}')
        # Здесь можно добавить логику редактирования товара
        current_app.logger.info('Товар успешно отредактирован')
        return redirect(url_for('admin.admin_panel'))
    current_app.logger.info(f'Открыта страница редактирования товара {product_id}')
    return render_template('admin/edit_product.html', product_id=product_id)

@bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    current_app.logger.info(f'Попытка удаления товара {product_id}')
    # Здесь можно добавить логику удаления товара
    current_app.logger.info('Товар успешно удален')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        data = request.form
        current_app.logger.info('Попытка добавления нового раздела')
        # Здесь можно добавить логику добавления раздела
        current_app.logger.info('Раздел успешно добавлен')
        return redirect(url_for('admin.admin_panel'))
    current_app.logger.info('Открыта страница добавления раздела')
    return render_template('admin/add_section.html')

@bp.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    current_app.logger.info(f'Попытка удаления раздела {section_id}')
    # Здесь можно добавить логику удаления раздела
    current_app.logger.info('Раздел успешно удален')
    return redirect(url_for('admin.admin_panel'))

@bp.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    if request.method == 'POST':
        data = request.form
        current_app.logger.info(f'Попытка редактирования раздела {section_id}')
        # Здесь можно добавить логику редактирования раздела
        current_app.logger.info('Раздел успешно отредактирован')
        return redirect(url_for('admin.admin_panel'))
    current_app.logger.info(f'Открыта страница редактирования раздела {section_id}')
    return render_template('admin/edit_section.html', section_id=section_id)

# API эндпоинты для управления порядком
@bp.route('/api/sections/reorder', methods=['POST'])
def reorder_sections():
    data = request.get_json()
    section_ids = data.get('section_ids', [])
    
    if not section_ids:
        current_app.logger.warning('Попытка обновить порядок секций без указания ID')
        return jsonify({"status": "error", "message": "Не указаны ID секций"})
    
    if db.reorder_sections(section_ids):
        current_app.logger.info('Порядок секций успешно обновлен')
        return jsonify({"status": "success"})
    else:
        current_app.logger.error('Ошибка при обновлении порядка секций')
        return jsonify({"status": "error", "message": "Ошибка при обновлении порядка"})

@bp.route('/api/products/reorder', methods=['POST'])
def reorder_products():
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    
    if not product_ids:
        current_app.logger.warning('Попытка обновить порядок товаров без указания ID')
        return jsonify({"status": "error", "message": "Не указаны ID товаров"})
    
    if db.reorder_products(product_ids):
        current_app.logger.info('Порядок товаров успешно обновлен')
        return jsonify({"status": "success"})
    else:
        current_app.logger.error('Ошибка при обновлении порядка товаров')
        return jsonify({"status": "error", "message": "Ошибка при обновлении порядка"})

@bp.route('/api/sections/<int:section_id>/order', methods=['PUT'])
def update_section_order(section_id):
    data = request.get_json()
    new_order = data.get('order')
    
    if new_order is None:
        current_app.logger.warning(f'Попытка обновить порядок секции {section_id} без указания нового порядка')
        return jsonify({"status": "error", "message": "Не указан новый порядок"})
    
    if db.update_section_order(section_id, new_order):
        current_app.logger.info(f'Порядок секции {section_id} успешно обновлен')
        return jsonify({"status": "success"})
    else:
        current_app.logger.error(f'Ошибка при обновлении порядка секции {section_id}')
        return jsonify({"status": "error", "message": "Ошибка при обновлении порядка"})

@bp.route('/api/products/<int:product_id>/order', methods=['PUT'])
def update_product_order(product_id):
    data = request.get_json()
    new_order = data.get('order')
    
    if new_order is None:
        current_app.logger.warning(f'Попытка обновить порядок товара {product_id} без указания нового порядка')
        return jsonify({"status": "error", "message": "Не указан новый порядок"})
    
    if db.update_product_order(product_id, new_order):
        current_app.logger.info(f'Порядок товара {product_id} успешно обновлен')
        return jsonify({"status": "success"})
    else:
        current_app.logger.error(f'Ошибка при обновлении порядка товара {product_id}')
        return jsonify({"status": "error", "message": "Ошибка при обновлении порядка"}) 