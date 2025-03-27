#!/bin/bash

# Переход в директорию скрипта
cd "$(dirname "$0")"

# Добавляем корневую директорию в PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Настройка переменных окружения для Flask
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Пути к файлам
BOT_SCRIPT="bot/main.py"
APP_SCRIPT="run.py"

# Функция для запуска бота
run_bot() {
    while true; do
        echo "Запуск бота..."
        python3 "$BOT_SCRIPT"
        if [ $? -eq 0 ]; then
            echo "Бот завершился успешно. Перезапуск через 5 секунд..."
        else
            echo "Бот завершился с ошибкой. Перезапуск через 5 секунд..."
        fi
        sleep 5
    done
}

# Функция для запуска Flask приложения
run_flask() {
    while true; do
        echo "Запуск Flask приложения..."
        FLASK_APP="$APP_SCRIPT" python3 -m flask run --host=0.0.0.0 --port=5050
        if [ $? -eq 0 ]; then
            echo "Приложение завершилось успешно. Перезапуск через 5 секунд..."
        else
            echo "Приложение завершилось с ошибкой. Перезапуск через 5 секунд..."
        fi
        sleep 5
    done
}

# Запуск процессов в фоновом режиме
run_bot &
BOT_PID=$!

run_flask &
FLASK_PID=$!

# Ожидание завершения процессов
trap "kill $BOT_PID $FLASK_PID" EXIT
wait 