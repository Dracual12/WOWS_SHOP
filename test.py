import requests

from bot.db import get_db_connection


def get_link():
    conn = get_db_connection()
    last_order = conn.execute('SELECT id FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    order_id = int(last_order['id'] + 10)
    last_cart = conn.execute('SELECT cart FROM orders ORDER BY id DESC LIMIT 1').fetchone()
    cart = int(last_cart['cart'])
    conn.close()
    url = f"https://alfa.rbsuat.com/payment/rest/register.do?token=157t7528u3o9bg0o9rljvu7dqs&orderNumber={order_id}&amount={cart}&returnUrl=192.168.0.1"
    try:
        response = requests.post(url)
        print(response.json()['formUrl'])
        if response.status_code == 200:
            return response
    except requests.RequestException as e:
        return {"error": f"Ошибка соединения: {str(e)}"}


get_link()