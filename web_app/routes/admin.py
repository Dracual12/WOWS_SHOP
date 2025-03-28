from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, session
from web_app import db
from ..utils.helpers import format_order_summary, order_text
from ..utils.telegram import send_telegram
from ..config import Config
from werkzeug.utils import secure_filename
import os
from ..utils.auth import admin_required, login_admin, logout_admin, is_admin_logged_in

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'])
@admin_required
def admin_panel():
    current_app.logger.info('Открыта панель администратора')
    return render_template('admin/index.html')

@bp.route('/order', methods=['GET'])
def order_management():
    current_app.logger.info('Открыта страница управления порядком')
    sections = db.get_sections()
    products = db.get_products()
    return render_template('admin/order.html', sections=sections, products=products)

@bp.route('/products', methods=['GET'])
@admin_required
def products():
    products = db.get_products()
    sections = db.get_sections()
    return render_template('admin/products.html', products=products, sections=sections)

@bp.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            section_id = request.form.get('section')
            review_links = request.form.get('review_link')
            order_index = int(request.form.get('order_index', 0))
            is_active = 'is_active' in request.form
            is_free = 'is_free' in request.form
            
            # Обработка цены
            if is_free:
                price = 0
            else:
                price = float(request.form.get('price', 0))
            
            # Обработка изображения
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                        raise ValueError('Файл слишком большой')
                    
                    filename = secure_filename(file.filename)
                    # Создаем директорию для изображений, если её нет
                    upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'products')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Сохраняем файл
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Сохраняем относительный путь для базы данных
                    image_path = os.path.join('static', 'images', 'products', filename)
                    current_app.logger.info(f'Изображение сохранено: {image_path}')
            
            if db.add_product(name, description, price, section_id, image_path, order_index, is_active, review_links):
                current_app.logger.info(f'Товар {name} успешно добавлен')
                return redirect(url_for('admin.products'))
            else:
                current_app.logger.error('Ошибка при добавлении товара')
                return render_template('admin/add_product.html', error='Ошибка при добавлении товара')
        except ValueError as e:
            current_app.logger.error(f'Ошибка валидации: {str(e)}')
            return render_template('admin/add_product.html', error=str(e))
        except Exception as e:
            current_app.logger.error(f'Ошибка при добавлении товара: {str(e)}')
            return render_template('admin/add_product.html', error='Произошла ошибка при добавлении товара')
    
    sections = db.get_sections()
    return render_template('admin/add_product.html', sections=sections)

@bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    current_app.logger.info(f'Редактирование товара: {product_id}')
    
    # Получаем товар
    products = db.get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        current_app.logger.error(f'Товар с ID {product_id} не найден')
        return redirect(url_for('admin.products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        section_id = int(request.form.get('section'))
        order_index = int(request.form.get('order_index', 0))
        is_active = request.form.get('is_active') == 'on'
        review_links = request.form.get('review_links')
        
        image = request.files.get('image')
        image_path = product.get('image')  # Сохраняем текущий путь к изображению
        
        if image:
            if image.content_length and image.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                return render_template('admin/edit_product.html', 
                                     product=product,
                                     sections=db.get_sections(),
                                     error='Размер файла превышает максимально допустимый (32MB)')
            
            filename = secure_filename(image.filename)
            image_path = os.path.join('static', 'images', 'products', filename)
            full_path = os.path.join(current_app.root_path, image_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            image.save(full_path)
            current_app.logger.info(f'Изображение сохранено: {image_path}')
        
        success = db.update_product(product_id, name, description, price, section_id, image_path, order_index, is_active, review_links)
        
        if success:
            current_app.logger.info('Товар успешно обновлен')
            return redirect(url_for('admin.products'))
        else:
            current_app.logger.error('Ошибка при обновлении товара')
            return render_template('admin/edit_product.html', 
                                 product=product,
                                 sections=db.get_sections(),
                                 error='Ошибка при обновлении товара')
    
    return render_template('admin/edit_product.html', 
                         product=product,
                         sections=db.get_sections())

@bp.route('/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    current_app.logger.info(f'Попытка удаления товара {product_id}')
    try:
        if db.delete_product(product_id):
            current_app.logger.info(f'Товар {product_id} успешно удален')
        else:
            current_app.logger.error(f'Ошибка при удалении товара {product_id}')
    except Exception as e:
        current_app.logger.error(f'Ошибка при удалении товара {product_id}: {str(e)}')
    
    return redirect(url_for('admin.products'))

@bp.route('/add_section', methods=['GET', 'POST'])
@admin_required
def add_section():
    if request.method == 'POST':
        name = request.form.get('name')
        order_index = int(request.form.get('order_index', 0))
        is_active = request.form.get('is_active') == 'on'
        
        success = db.add_section(name, order_index, is_active)
        
        if success:
            current_app.logger.info('Раздел успешно добавлен')
            return redirect(url_for('admin.admin_panel'))
        else:
            current_app.logger.error('Ошибка при добавлении раздела')
            return render_template('admin/add_section.html', error='Ошибка при добавлении раздела')
    
    return render_template('admin/add_section.html')

@bp.route('/delete_section/<int:section_id>', methods=['POST'])
@admin_required
def delete_section(section_id):
    success = db.delete_section(section_id)
    
    if success:
        current_app.logger.info(f'Раздел {section_id} успешно удален')
    else:
        current_app.logger.error(f'Ошибка при удалении раздела {section_id}')
    
    return redirect(url_for('admin.admin_panel'))

@bp.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
@admin_required
def edit_section(section_id):
    section = db.get_section(section_id)
    if not section:
        current_app.logger.error(f'Раздел {section_id} не найден')
        return redirect(url_for('admin.admin_panel'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        order_index = int(request.form.get('order_index', 0))
        is_active = request.form.get('is_active') == 'on'
        
        success = db.update_section(section_id, name, order_index, is_active)
        
        if success:
            current_app.logger.info(f'Раздел {section_id} успешно обновлен')
            return redirect(url_for('admin.admin_panel'))
        else:
            current_app.logger.error(f'Ошибка при обновлении раздела {section_id}')
            return render_template('admin/edit_section.html', 
                                 section=section,
                                 error='Ошибка при обновлении раздела')
    
    return render_template('admin/edit_section.html', section=section)

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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            login_admin()
            return redirect(url_for('admin.admin_panel'))
        else:
            current_app.logger.warning('Неудачная попытка входа в админ-панель')
            return render_template('admin/login.html', error='Неверное имя пользователя или пароль')
    
    if is_admin_logged_in():
        return redirect(url_for('admin.admin_panel'))
    
    return render_template('admin/login.html')

@bp.route('/logout')
def logout():
    logout_admin()
    return redirect(url_for('admin.login'))

@bp.route('/sections', methods=['GET'])
@admin_required
def sections():
    sections = db.get_sections()
    return render_template('admin/sections.html', sections=sections) 