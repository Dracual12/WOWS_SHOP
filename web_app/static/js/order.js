document.addEventListener("DOMContentLoaded", () => {
    const checkoutButton = document.getElementById("checkout-button");

    checkoutButton.addEventListener("click", async () => {
    if (window.Telegram && window.Telegram.WebApp) {
        console.log("Telegram WebApp script is loaded!");
        (window.Telegram.WebApp.initDataUnsafe.user.id);}
        // Выводим Telegram ID в консоль сервера, отправив его через fetch



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
                <input type="text" id="order-input" placeholder="Введите данные..." />
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
            // let otpData = document.getElementById("order-input").value;
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
            alert("Ссылка для связи: " + telegramLink);
            popup.remove();

            // После ввода ссылки, запрашиваем с сервера последнюю запись заказа для текущего Telegram ID
            fetchLatestOrder(1456241115);
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

        popup.querySelector(".confirm-btn").addEventListener("click", () => {
            // Закрываем Telegram Web App
            if (window.Telegram && window.Telegram.WebApp) {
                window.Telegram.WebApp.close();
            }
        });
    }
});
