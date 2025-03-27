from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from ..models.database import db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET'])
def admin_panel():
    return render_template('admin/index.html')

@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = request.form
        # Здесь можно добавить логику добавления товара
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin/add_product.html')

@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        data = request.form
        # Здесь можно добавить логику редактирования товара
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin/edit_product.html', product_id=product_id)

@bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    # Здесь можно добавить логику удаления товара
    return redirect(url_for('admin.admin_panel'))

@bp.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        data = request.form
        # Здесь можно добавить логику добавления раздела
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin/add_section.html')

@bp.route('/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    # Здесь можно добавить логику удаления раздела
    return redirect(url_for('admin.admin_panel'))

@bp.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    if request.method == 'POST':
        data = request.form
        # Здесь можно добавить логику редактирования раздела
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin/edit_section.html', section_id=section_id) 