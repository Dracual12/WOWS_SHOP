import asyncio

# Создаем общий цикл событий
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Функция для получения общего цикла
def get_shared_loop():
    global loop
    print("Shared loop is running:", loop.is_running())
    return loop

# Функция для запуска цикла
def run_loop():
    global loop
    print("Starting shared loop...")
    loop.run_forever()

# Функция для остановки цикла
def stop_loop():
    global loop
    print("Stopping shared loop...")
    loop.stop()