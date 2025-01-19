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
        SELECT p.name, c.quantity, (p.price * c.quantity) AS total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in cart])




@app.route('/api/cart/<int:product_id>', methods=['PUT'])
def update_cart_quantity(product_id):
    data = request.get_json()
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        return jsonify({"error": "Некорректное количество"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE cart SET quantity = ? WHERE product_id = ?', (quantity, product_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Количество товара обновлено"})



@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
def delete_cart_item(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Товар удалён из корзины"})



@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('admin.html', products=products)


# API для управления секциями и товарами
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.files.get('image')

        if not name or not price or not image:
            return "Все поля обязательны!", 400

        # Сохранение изображения
        image_path = f'static/images/{image.filename}'
        image.save(image_path)

        # Добавление товара в базу данных
        conn = get_db_connection()

        try:
            conn.execute('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', (name, float(price), image_path))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")

        return redirect('/admin')

    return render_template('add_product.html')


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




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
