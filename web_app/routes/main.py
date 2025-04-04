import time

from flask import Blueprint, render_template, request, jsonify, current_app
from web_app import db
from ..utils.helpers import format_order_summary, order_text
from ..utils.telegram import send_telegram, edit_telegram_message
from ..config import Config

bp = Blueprint('main', __name__)
from bot.db import get_db_connection
import requests
import json
from ..config import Config


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
def get_link(user, login, password):
    conn = get_db_connection()
    conn.execute("INSERT INTO orders (user_id) VALUES (?)", (user,))
    conn.commit()
    last_order = conn.execute('SELECT id FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user,)).fetchone()[0]
    print(last_order)
    order_id = int(last_order) + 102075
    last_cart = db.get_cart_items(user)

    total = sum(item['price'] * item['quantity'] for item in last_cart)
    conn.close()

    url = f"https://payment.alfabank.ru/payment/rest/register.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderNumber={order_id}&amount={int(total) * 100}&returnUrl=https://t.me/armada_gold_bot"
    response = requests.get(url)
    text = response.text
    try:
        k = json.loads(text)  # Ручное преобразование текста в JSON
    except json.JSONDecodeError as e:
        print("Ошибка при декодировании JSON:", e)
        return
    print(k)
    if 'formUrl' in k:
        a = k['formUrl']
        k2 = send_telegram(Config.BOT_TOKEN, user,
                           "Нажимая «Оплатить» Вы принимаете положения Политики Конфиденциальности и Пользовательского Соглашения",
                           pay(a))
        conn = get_db_connection()
        conn.execute('UPDATE users SET message_id = ? WHERE telegram_id = ?', (k2, user))
        conn.commit()
        conn.close()
        check(k['orderId'], user, login, password)
    else:
        print("Ключ 'formUrl' отсутствует в словаре k:", k)


# Получение текста заказа

# Проверка статуса оплаты
def check(orderId, user, login, password):
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
        time.sleep(interval)

    conn = get_db_connection()
    if glag:
        edit_telegram_message(Config.BOT_TOKEN, user,
                              conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0],
                              'Заказ успешно оплачен!')
        conn.execute("DELETE FROM cart WHERE user_id = ?", (user,))
        conn.commit()
        data = order_text(user)
        message = f"""
        Детали заказа:
        ———————————————
        🆔 ID заказа: {data['id']}
        👤 User ID: id <a href="tg://user?id={data['user_id']}">{data['user_id']}</a>
        🛒 Корзина: {data['cart']}
        🔑 Логин;Пароль: {login}:{password}
        ———————————————
        Спасибо за ваш заказ! 😊
        """
        send_telegram( Config.BOT_TOKEN, Config.ADMIN_ID, message)
    else:
        edit_telegram_message(Config.BOT_TOKEN, user,
                              conn.execute('SELECT message_id FROM users WHERE telegram_id = ?', (user,)).fetchone()[0],
                              'Время на оплату истекло')
        url2 = f'https://payment.alfabank.ru/payment/rest/getOrderStatus.do?token=oj5skop8tcf9a8mmoh9ssb31ei&orderId={orderId}'
        requests.get(url2)


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
    user = data.get('user_id')
    login = data.get('login')
    password = data.get('password')
    print(data)
    if user and login and password:
        current_app.logger.info(f'Оформлен заказ от пользователя: {user}')
        get_link(user, login, password)
    else:
        current_app.logger.warning('Попытка оформить заказ с неполными данными')

    return jsonify({"status": "error"})


@bp.route('/api/order/latest', methods=['POST'])
def get_latest_order():
    current_app.logger.info('Запрос последнего заказа')
    return jsonify({"status": "success"})


@bp.route('/product/<int:product_id>')
def product_page(product_id):
    """Страница отдельного товара"""
    try:
        # Получаем все товары
        products = db.get_products()
        current_app.logger.info(f"Получены товары: {products}")
        current_app.logger.info(f"Ищем товар с ID: {product_id}")

        # Находим нужный товар
        product = next((p for p in products if p['id'] == product_id), None)
        current_app.logger.info(f"Найденный товар: {product}")

        if product:
            # Получаем данные пользователя из URL
            tg_id = request.args.get('tg_id')
            first_name = request.args.get('first_name')
            last_name = request.args.get('last_name')
            username = request.args.get('username')
            language_code = request.args.get('language_code')
            start_param = request.args.get('start_param')
            auth_date = request.args.get('auth_date')
            hash = request.args.get('hash')

            # Преобразуем tg_id в число
            if tg_id:
                try:
                    tg_id = int(tg_id)
                except ValueError:
                    current_app.logger.error(f"Неверный формат tg_id: {tg_id}")
                    tg_id = None

            # Преобразуем auth_date в число
            if auth_date:
                try:
                    auth_date = int(auth_date)
                except ValueError:
                    current_app.logger.error(f"Неверный формат auth_date: {auth_date}")
                    auth_date = None

            current_app.logger.info(f"Открыта страница товара {product_id} для пользователя {tg_id}")
            return render_template('product.html',
                                   product=product,
                                   tg_id=tg_id,
                                   first_name=first_name,
                                   last_name=last_name,
                                   username=username,
                                   language_code=language_code,
                                   start_param=start_param,
                                   auth_date=auth_date,
                                   hash=hash)
        else:
            current_app.logger.warning(f"Товар с ID {product_id} не найден")
            return render_template('product.html', product=None)

    except Exception as e:
        current_app.logger.error(f"Ошибка при открытии страницы товара: {str(e)}")
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


@bp.route('/order', methods=['GET'])
def order_form():
    """Отображает форму заказа"""
    tg_id = request.args.get('tg_id')
    if not tg_id:
        return jsonify({"status": "error", "message": "Не указан ID пользователя"}), 400

    # Получаем товары из корзины
    cart_items = db.get_cart_items(tg_id)
    if not cart_items:
        return jsonify({"status": "error", "message": "Корзина пуста"}), 400

    # Вычисляем общую сумму
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('order_form.html',
                           cart_items=cart_items,
                           total_price=total_price)


@bp.route('/api/order', methods=['POST'])
def create_order():
    """Создает новый заказ"""
    try:
        data = request.get_json()
        required_fields = ['user_id', 'login', 'password']

        # Проверяем наличие всех необходимых полей
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Отсутствует обязательное поле: {field}"}), 400

        # Получаем товары из корзины
        cart_items = db.get_cart_items(data['user_id'])
        if not cart_items:
            return jsonify({"status": "error", "message": "Корзина пуста"}), 400

        # Вычисляем общую сумму
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)

        # Создаем заказ
        order_id = db.create_order(
            user_id=data['user_id'],
            login=data['login'],
            password=data['password'],
            items=cart_items,
            total_price=total_price
        )

        if order_id:
            # Очищаем корзину
            db.clear_cart(data['user_id'])
            return jsonify({"status": "success", "order_id": order_id})
        else:
            return jsonify({"status": "error", "message": "Ошибка при создании заказа"}), 500

    except Exception as e:
        current_app.logger.error(f"Ошибка при создании заказа: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
