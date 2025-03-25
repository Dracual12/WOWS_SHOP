import asyncio
import logging
import sys
import os
import json
import time

import requests

from bot import config

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
if project_root not in sys.path:
    sys.path.append(project_root)


def edit_telegram_message(
        BOT_TOKEN: str,
        chat_id: str,
        message_id: int,
        new_text: str,
        reply_markup=None,
        parse_mode="HTML"
):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": parse_mode
    }

    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, params=params).json()

    if response.get("ok"):
        return True
    else:
        print("Ошибка редактирования:", response)
        return False

def send_telegram(text: str, BOT_TOKEN: str, CHAT_ID: str, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",  # или "MarkdownV2"
    }

    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, params=params).json()

    if response.get("ok"):
        return response["result"]["message_id"]  # Возвращаем message_id
    else:
        print("Ошибка отправки:", response)
        return None


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, FSInputFile
# Клавиатура для оплаты
def pay(link):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Оплатить", "url": f"{link}"},
                {"text": "Пользовательское соглашение", "url": "https://clck.ru/3GgzNq"}
            ],
            [
                {"text": "Политика конфиденциальности", "url": "https://clck.ru/3GHACe"}
            ]
        ]
    }
    return keyboard

# Получение ссылки на оплату
def get_link(user):
    print(user)
    conn = get_db_connection()
    last_order = conn.execute('SELECT id FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user,)).fetchone()
    order_id = int(dict(last_order)['id']) + 100060
    last_cart = conn.execute('SELECT cart FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    last_cart = dict(last_cart)
    cart = int((last_cart['cart'].split('Итого:')[1]).split()[0])
    conn.close()

    url = f"https://payment.alfabank.ru/payment/rest/register.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderNumber={order_id}&amount={cart}&returnUrl=https://t.me/armada_gold_bot"
    response = requests.get(url)
    text = response.text
    try:
        k = json.loads(text)  # Ручное преобразование текста в JSON
    except json.JSONDecodeError as e:
        print("Ошибка при декодировании JSON:", e)
        return  # Прекращаем выполнение, если текст не является JSON

    if 'formUrl' in k:
        a = k['formUrl']
        k2 = send_telegram("Нажимая «Оплатить» Вы принимаете положения Политики Конфиденциальности и Пользовательского Соглашения", BOT_TOKEN, user, pay(a))
        conn = get_db_connection()
        conn.execute('UPDATE users SET message_id = ? WHERE telegram_id = ?', (k2, user))
        conn.commit()
        conn.close()
        check(k['orderId'], user)
    else:
        print("Ключ 'formUrl' отсутствует в словаре k:", k)
# Получение текста заказа
def order_text(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (user,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    else:
        return None

# Проверка статуса оплаты
def check(orderId, user):
    url = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
    start_time = time.time()
    duration = 5 * 60  # 5 минут
    interval = 5  # Интервал проверки (5 секунд)
    glag = False

    while time.time() - start_time < duration:
        try:
            response = requests.get(url)

            data = response.json()
            if data['OrderStatus'] == 2:
                glag = True
                break
        except Exception as e:
            print(f"Ошибка при запросе статуса заказа: {e}")

    conn = get_db_connection()
    if glag:
        edit_telegram_message(BOT_TOKEN, user, conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0], 'Заказ успешно оплачен!')
        conn.execute("DELETE FROM cart WHERE user_id = ?", (user,))
        conn.commit()
        data = order_text(user)
        message = f"""
        Детали заказа:
        ———————————————
        🆔 ID заказа: {data['id']}
        👤 User ID: id <a href="tg://user?id={data['user_id']}">{data['user_id']}</a>
        🛒 Корзина: {data['cart']}
        🔑 OTP-код: {data['otp_code']}
        ———————————————
        Спасибо за ваш заказ! 😊
        """
        send_telegram(message, BOT_TOKEN, config.ADMIN_ID)
    else:
        edit_telegram_message(BOT_TOKEN, user, conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0], 'Время на оплату истекло')
        url2 = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
        requests.get(url2)


from bot.db import get_db_connection
from flask import Flask, render_template, request, jsonify, redirect, url_for
BOT_TOKEN = "7574071837:AAFE0A2rW27YmxOi40AG68577fK3zluinu4"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)







# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


@app.route("/save-tg-id", methods=["POST"])
def save_tg_id():
    data = request.get_json()  # Получаем данные из запроса
    tg_id = data.get("tg_id")
    conn = get_db_connection()
    req = conn.execute("INSERT INTO orders (user_id) VALUES (?)", (tg_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': "cool"})


def format_order_summary(order_items):
    #Итоговая стоимость
    order_items = json.loads(order_items)
    total_sum = sum(int(item['total']) for item in order_items)

    # Формируем текст для каждого товара
    items_text = []
    for item in order_items:
        # Убираем Unicode-символы (например, \u0437) и декодируем строку
        name = item['name'].encode('unicode_escape').decode('unicode_escape')
        items_text.append(f"{name} - {item['quantity']} шт. - {item['total']} руб.")

    # Объединяем все строки с товарами
    items_summary = "\n".join(items_text)

    # Добавляем итоговую стоимость
    final_text = f"{items_summary}\n\nИтого: {total_sum} руб."

    return final_text

@app.route('/save-otp', methods=['POST'])
def save_otp():
    data = request.get_json()  # Получаем данные из запроса
    user_id = data.get("tg_id")
    otp = data.get("otp")
    conn = get_db_connection()
    conn.execute("""
            UPDATE orders
            SET otp_code = ?
            WHERE user_id = (
                    SELECT user_id
                FROM orders
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 1
                )
        """, (otp, user_id))
    conn.commit()
    cart = conn.execute('''
                SELECT p.id, p.name, c.quantity, (p.price * c.quantity) AS total
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
            ''', (user_id,)).fetchall()
    cart2 = format_order_summary(json.dumps([dict(row) for row in cart]))

    conn.execute("""UPDATE orders SET cart = ? WHERE user_id = 
        (SELECT user_id
    FROM orders
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 1
    )""", (cart2, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': "cool"})


@app.route('/save_tg_link', methods=['POST'])
def save_link():
    data = request.get_json()  # Получаем данные из запроса
    user_id = data.get("tg_id")
    tg_link = data.get("link")
    conn = get_db_connection()
    conn.execute("""
            UPDATE orders
            SET telegram_link = ?
            WHERE user_id = (SELECT user_id
    FROM orders
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 1
    )
        """, (tg_link, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': "cool"})



@app.route('/api/order/end', methods=['POST'])
def some_route():
    data = request.get_json()  # Получаем данные из запроса
    tg = data.get("telegram_id")

    if not tg:
        return jsonify({"error": "telegram_id is required"}), 400
    get_link(tg)
    # Возвращаем ответ сразу после запуска потока
    return jsonify({"message": "Запрос принят в обработку", "telegram_id": tg}), 202




@app.route('/api/order/latest', methods=['POST'])
def get_latest_order():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({"error": "Telegram ID не передан"}), 400

    conn = get_db_connection()
    # Получаем последнюю запись заказа по telegram_id, сортируя по id в порядке убывания
    order = conn.execute('''
        SELECT id, user_id, cart, otp_code, telegram_link
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (telegram_id,)).fetchone()
    conn.close()

    if order is None:
        return jsonify({"error": "Заказ не найден"}), 404

    return jsonify(dict(order))

# API для добавления товара в корзину
@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
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

@app.route('/api/cart2', methods=['POST'])
def add_to_cart2():
    data = request.get_json()
    telegram_id = data.get('telegram_id')
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
    user_id = request.args.get("tg_id")
    cart = conn.execute('''
        SELECT p.id, p.name, c.quantity, (p.price * c.quantity) AS total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in cart])

@app.route('/api/cart2', methods=['GET'])
def get_cart2():
    conn = get_db_connection()
    user_id = request.args.get("tg_id")
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
    user = data.get('tg')
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        return jsonify({"error": "Некорректное количество"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE cart SET quantity = ? WHERE user_id = ?', (quantity, user))
    conn.commit()
    conn.close()

    return jsonify({"message": "Количество товара обновлено"})

@app.route('/api/cart2/<int:product_id>', methods=['PUT'])
def update_cart_quantity2(product_id):
    data = request.get_json()
    user = data.get('tg')
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        return jsonify({"error": "Некорректное количество"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE cart SET quantity = ? WHERE user_id = ?', (quantity, user))
    conn.commit()
    conn.close()

    return jsonify({"message": "Количество товара обновлено"})

@app.route('/api/cart/<int:tgId>/<int:product_id>', methods=['DELETE'])
def delete_cart_item(tgId, product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (tgId,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Товар удалён из корзины"})


@app.route('/api/cart2/<int:tgId>/<int:product_id>', methods=['DELETE'])
def delete_cart_item2(tgId, product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE user_id = ?', (tgId,))
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
    conn = get_db_connection()

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            price = request.form.get('price')
            description = request.form.get('description')
            image = request.files.get('image')
            review_link = request.form.get('review_link', '')  # Получаем ссылку на обзор (по умолчанию пустая)
            alternative_goods = request.form.getlist('alternative_goods')  # Получаем список альтернативных товаров
            section_id = request.form.get('section_id')

            # Проверяем, выбрана ли секция и существует ли она
            section_row = conn.execute("SELECT name FROM sections WHERE id = ?", (section_id,)).fetchone()
            if not section_row:
                return "Ошибка: выбранная секция не найдена.", 400
            section = section_row['name']

            # Проверка обязательных полей
            if not name or not price or not image or not section_id:
                return "Все обязательные поля должны быть заполнены!", 400

            # Сохранение изображения
            image_path = f'static/images/{image.filename}'
            image.save(image_path)

            # Преобразуем список альтернативных товаров в строку (через запятую)
            alternative_goods_str = ','.join(alternative_goods) if alternative_goods else None

            # Добавляем товар в базу данных
            conn.execute(
                '''INSERT INTO products (name, price, description, image, section, review_link, alternative_goods)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, float(price), description, image_path, section, review_link, alternative_goods_str)
            )
            conn.commit()
            return redirect('/admin')

        except Exception as e:
            print(f"Ошибка при добавлении товара: {e}")
            return "Ошибка на сервере", 500

        finally:
            conn.close()

    # Динамическая загрузка секций для отображения в форме
    sections = conn.execute("SELECT id, name FROM sections").fetchall()
    conn.close()

    return render_template('add_product.html', sections=sections)



# Маршрут для редактирования товара
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    if request.method == 'POST':
        # Получение данных из формы
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        review_link = request.form.get('review_link', '')  # Новое поле для ссылки на обзор
        section_id = request.form['section_id']

        # Получение названия секции
        section = conn.execute("SELECT name FROM sections WHERE id = ?", (section_id,)).fetchone()['name']

        # Обработка загрузки изображения
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename:  # Если файл загружен
            # Сохраняем файл в папку uploads
            filename = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(filename)
            image_url = f"/static/uploads/{image_file.filename}"

        # Обновление данных в базе
        if image_url:
            # Если загружено новое изображение, обновляем его URL
            conn.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, section = ?, review_link = ?, image_url = ?
                WHERE id = ?
            ''', (name, price, description, section, review_link, image_url, product_id))
        else:
            # Если изображение не загружено, оставляем старое
            conn.execute('''
                UPDATE products 
                SET name = ?, price = ?, description = ?, section = ?, review_link = ?
                WHERE id = ?
            ''', (name, price, description, section, review_link, product_id))

        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))  # Перенаправляем в админ-панель

    else:
        # Получение текущих данных товара для отображения в форме
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        sections = conn.execute('SELECT * FROM sections').fetchall()  # Получаем все секции
        conn.close()
        return render_template('edit_product.html', product=product, sections=sections)

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

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    # Здесь вы можете сохранить данные заказа в базе
    user_id = request.json.get('telegram_id')
    contact_info = data.get("contactInfo")
    otp_code = data.get("otpCode")
    telegram_link = data.get("telegramLink")

    # Сохранение данных в базу данных
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO orders (user_id, contact_info, otp_code, telegram_link) VALUES (?, ?, ?, ?)',
        (user_id, contact_info, otp_code, telegram_link),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
