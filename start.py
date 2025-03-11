import asyncio
import threading

# Глобальная переменная для хранения цикла событий
_loop = None

# Функция для получения общего цикла
def get_shared_loop():
    global _loop
    if _loop is None:
        print("Initializing shared loop...")
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

        # Функция для запуска цикла событий в отдельном потоке
        def start_loop():
            print("Starting event loop in a separate thread...")
            _loop.run_forever()

        # Запускаем цикл событий в отдельном потоке
        threading.Thread(target=start_loop, daemon=True).start()
    else:
        print("Getting shared loop...")
    return _loop