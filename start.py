import asyncio
import threading

# Создаем общий цикл событий
loop = asyncio.new_event_loop()

# Функция для запуска цикла событий в отдельном потоке
def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Запускаем цикл событий в отдельном потоке
threading.Thread(target=start_loop, daemon=True).start()

# Функция для получения общего цикла
def get_shared_loop():
    return loop