from db import get_db_connection
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)

# Корзина (временно хранится в памяти)
cart = []



# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# API для добавления товара в корзину
@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    telegram_id = data.get("userTelegramId")  # Telegram ID передаётся через запрос
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # Проверяем, существует ли пользователь с этим Telegram ID
    conn = get_db_connection()
    user = conn.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id = telegram_id # Получаем внутренний ID пользователя

    # Добавляем товар в корзину
    conn.execute('''
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
    ''', (user_id, product_id, quantity, quantity))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product added to cart"})





# API для просмотра корзины
@app.route('/api/cart', methods=['GET'])
def get_cart():
    conn = get_db_connection()
    user_id = 1456241115  # Используйте ID текущего пользователя
    cart = conn.execute('''
        SELECT p.id, p.name, c.quantity, (p.price * c.quantity) AS total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in cart])




@app.route('/api/cart/<int:product_id>', methods=['PUT'])
def update_cart_quantity(product_id):
    data = request.get_json()
    user = 1456241115
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        return jsonify({"error": "Некорректное количество"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE cart SET quantity = ? WHERE user_id = ?', (quantity, user))
    conn.commit()
    conn.close()

    return jsonify({"message": "Количество товара обновлено"})



@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
def delete_cart_item(product_id):
    user = 1456241115
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (user,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Товар удалён из корзины"})



@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    sections = conn.execute('SELECT * FROM sections').fetchall()
    conn.close()
    return render_template('admin.html', products=products, sections=sections)


# API для управления секциями и товарами
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        conn = get_db_connection()
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('image')
        section = [dict(row) for row in
                   conn.execute("SELECT name FROM sections WHERE id = ?", (request.form['section_id'],)).fetchall()][0][
            'name']

        if not name or not price or not image:
            return "Все поля обязательны!", 400

        # Сохранение изображения
        image_path = f'static/images/{image.filename}'
        image.save(image_path)

        # Добавление товара в базу данных
        conn = get_db_connection()

        try:
            conn.execute('INSERT INTO products (name, price, description, image, section) VALUES (?, ?, ?, ?, ?)', (name, float(price), description, image_path, section))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")

        return redirect('/admin')

    return render_template('add_product.html')


# Маршрут для редактирования товара
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    if request.method == 'POST':
        # Получение данных из формы
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        # Обновление данных в базе
        section = [dict(row) for row in conn.execute("SELECT name FROM sections WHERE id = ?", (request.form['section_id'],)).fetchall()][0]['name']
        conn.execute('UPDATE products SET name = ?, price = ?, description = ?, section = ? WHERE id = ?',
                     (name, price, description, section, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    else:
        # Получение текущих данных товара для отображения в форме
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        return render_template('edit_product.html', product=product)

# Маршрут для удаления товара
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))


# API: Get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(row) for row in products])




@app.route('/product/<int:product_id>')
def product_page(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if not product:
        return "Товар не найден", 404
    return render_template('product.html', product=product)

@app.route('/api/sections', methods=['GET'])
def get_sections_with_products():
    conn = get_db_connection()

    # Получаем секции с товарами
    sections = conn.execute('''
        SELECT s.id AS section_id, s.name AS section_name,
               p.id AS product_id, p.name AS product_name, p.price, p.image
        FROM sections s
        LEFT JOIN products p ON s.name = p.section
        ORDER BY s.id, p.id
    ''').fetchall()
    conn.close()

    # Группируем товары по секциям
    data = {}
    for row in sections:
        section_id = row['section_id']
        if section_id not in data:
            data[section_id] = {
                'section_name': row['section_name'],
                'products': []
            }
        if row['product_id']:
            data[section_id]['products'].append({
                'id': row['product_id'],
                'name': row['product_name'],
                'price': row['price'],
                'image': row['image']
            })
    return jsonify(data)


@app.route('/api/viewsections', methods=['GET'])
def view_sections():
    conn = get_db_connection()
    sections = conn.execute('SELECT id, name FROM sections').fetchall()
    conn.close()

    return jsonify([{"id": row["id"], "name": row["name"]} for row in sections])
@app.route('/admin/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            return "Все поля обязательны!", 400

        conn = get_db_connection()

        try:
            conn.execute('INSERT INTO sections (name) VALUES (?)', (name,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")

        return redirect('/admin')

    return render_template('add_section.html')

@app.route('/admin/delete_section/<int:section_id>', methods=['POST'])
def delete_section(section_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM sections WHERE id = ?", (section_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))


@app.route('/admin/edit_section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        conn.execute('UPDATE sections SET name = ? WHERE id = ?',
                     (name,section_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    else:
        # Получение текущих данных товара для отображения в форме
        section = conn.execute('SELECT * FROM sections WHERE id = ?', (section_id,)).fetchone()
        conn.close()
        return render_template('edit_section.html', section=section)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
