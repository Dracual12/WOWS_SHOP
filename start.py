import asyncio
import threading

# Проверяем, был ли цикл событий уже создан
if not hasattr(asyncio, '_shared_loop'):
    print("Initializing shared loop...")
    # Создаем общий цикл событий
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Сохраняем цикл событий в модуле
    asyncio._shared_loop = loop

    # Функция для запуска цикла событий в отдельном потоке
    def start_loop():
        print("Starting event loop in a separate thread...")
        loop.run_forever()

    # Запускаем цикл событий в отдельном потоке
    threading.Thread(target=start_loop, daemon=True).start()

# Функция для получения общего цикла
def get_shared_loop():
    print("Getting shared loop...")
    return asyncio._shared_loop