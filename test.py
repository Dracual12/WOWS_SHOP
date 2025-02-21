import requests


def get_iiko_menu():
    url = f"https://alfa.rbsuat.com/payment/rest/register.do?token=157t7528u3o9bg0o9rljvu7dqs&orderNumber=100&amount=1000&returnUrl=192.168.0.1"
    try:
        response = requests.post(url)
        print(response)
        if response.status_code == 200:
            print(response.text)
    except requests.RequestException as e:
        return {"error": f"Ошибка соединения: {str(e)}"}


get_iiko_menu()