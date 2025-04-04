console.log('Загрузка cart2.js');

// Функция обновления количества товара
window.updateCartQuantity = function(productId, newQuantity, li) {
    if (!productId && li) {
        productId = li.getAttribute('data-product-id');
    }
    
    if (!productId) {
        console.error('Не удалось получить ID товара');
        return;
    }

    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    if (!tgId) {
        console.error('Не удалось получить tg_id');
        return;
    }

    console.log('Отправка запроса на обновление количества:', {
        productId,
        newQuantity,
        tgId
    });
    
    fetch(`/api/cart/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity, tg_id: tgId }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка обновления корзины');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                const unitPrice = parseFloat(li.getAttribute('data-unit-price'));
                li.querySelector('.quantity-value').textContent = newQuantity;
                li.querySelector('.item-total').textContent = (unitPrice * newQuantity).toFixed(2) + ' рублей';
                window.loadCartItems();
                showNotification('Количество обновлено', 'success');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification('Ошибка при обновлении корзины', 'error');
        });
};

// Функция удаления товара из корзины
window.removeCartItem = function(productId, li) {
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    if (!tgId) {
        console.error('Не удалось получить tg_id');
        return;
    }
    
    fetch(`/api/cart/${tgId}/${productId}`, {
        method: 'DELETE',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка удаления товара из корзины');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                window.loadCartItems();
                showNotification('Товар удален из корзины', 'success');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification('Ошибка при удалении товара', 'error');
        });
};

// Функция добавления товара в корзину
window.addToCart = async function(productId) {
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    if (!tgId) {
        console.error('Не удалось получить tg_id');
        return;
    }

    console.log('Вызов функции addToCart с параметрами:', { productId, tgId });
    try {
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1,
                tg_id: tgId
            })
        });

        console.log('Ответ сервера:', response.status);
        
        if (response.ok) {
            showNotification('Товар добавлен в корзину', 'success');
            window.loadCartItems();
        } else {
            throw new Error('Ошибка при добавлении товара в корзину');
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        showNotification('Ошибка при добавлении товара', 'error');
    }
};

// Функция оформления заказа
window.checkout = function() {
    console.log('Функция checkout вызвана');
    try {
        const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
        if (!tgId) {
            console.error('Не удалось получить ID пользователя');
            return;
        }
        
        console.log('Перенаправление на форму заказа с ID:', tgId);
        window.location.href = `/order?tg_id=${tgId}`;
    } catch (error) {
        console.error('Ошибка при оформлении заказа:', error);
        showNotification('Ошибка при оформлении заказа', 'error');
    }
}

// Функция загрузки товаров корзины
window.loadCartItems = function() {
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    
    if (!cartItemsContainer || !cartTotalElement) {
        console.error('Элементы корзины не найдены');
        return;
    }

    // Получаем tg_id из Telegram WebApp
    let tgId;
    try {
        tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
        console.log('Получен tg_id из WebApp:', tgId);
    } catch (error) {
        console.error('Ошибка при получении tg_id из WebApp:', error);
        // Если не удалось получить tg_id из WebApp, пробуем получить из URL
        const urlParams = new URLSearchParams(window.location.search);
        tgId = urlParams.get('tg_id');
        console.log('Получен tg_id из URL:', tgId);
    }

    if (!tgId) {
        console.error('tg_id не найден');
        return;
    }

    // Используем request вместо fetch
    request(`/api/cart?tg_id=${tgId}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.success) {
            const cartItems = response.cart_items;
            const total = response.total;
            
            // Очищаем контейнер
            cartItemsContainer.innerHTML = '';
            
            if (cartItems.length === 0) {
                cartItemsContainer.innerHTML = '<li class="cart-item">Корзина пуста</li>';
                cartTotalElement.innerHTML = '';
            } else {
                // Добавляем каждый товар
                cartItems.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'cart-item';
                    li.innerHTML = `
                        <div class="cart-item-content">
                            <div class="cart-item-info">
                                <span class="cart-item-name">${item.name}</span>
                                <span class="cart-item-price">${item.price} ₽</span>
                            </div>
                            <div class="cart-item-controls">
                                <button class="quantity-btn minus" data-id="${item.id}">-</button>
                                <span class="quantity">${item.quantity}</span>
                                <button class="quantity-btn plus" data-id="${item.id}">+</button>
                                <button class="remove-btn" data-id="${item.id}">×</button>
                            </div>
                        </div>
                    `;
                    cartItemsContainer.appendChild(li);
                });
                
                // Добавляем итоговую сумму
                cartTotalElement.innerHTML = `
                    <div class="cart-total-content">
                        <span>Итого:</span>
                        <span class="total-amount">${total} ₽</span>
                    </div>
                    <button class="checkout-btn" onclick="checkout()">Оформить заказ</button>
                `;
            }
        } else {
            console.error('Ошибка при загрузке корзины:', response.error);
        }
    })
    .catch(error => {
        console.error('Ошибка при загрузке корзины:', error);
    });
};

// Функция показа уведомлений
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Инициализация Telegram WebApp
const dataElement = document.getElementById('telegram-data');
if (!dataElement) {
    console.error('Элемент telegram-data не найден');
} else {
    const userData = {
        id: dataElement.dataset.tgId === 'null' ? null : Number(dataElement.dataset.tgId),
        first_name: dataElement.dataset.firstName || null,
        last_name: dataElement.dataset.lastName || null,
        username: dataElement.dataset.username || null,
        language_code: dataElement.dataset.languageCode || null,
        start_param: dataElement.dataset.startParam || null,
        auth_date: dataElement.dataset.authDate === 'null' ? null : Number(dataElement.dataset.authDate),
        hash: dataElement.dataset.hash || null
    };

    console.log('Инициализация Telegram WebApp с данными:', userData);

    // Проверяем, что Telegram WebApp уже существует
    if (window.Telegram && window.Telegram.WebApp) {
        console.log('Telegram WebApp уже инициализирован');
        window.Telegram.WebApp.initDataUnsafe.user = userData;
        // Загружаем корзину сразу, если WebApp уже инициализирован и функция существует
        if (userData.id && typeof window.loadCartItems === 'function') {
            window.loadCartItems();
        }
    } else {
        window.Telegram = {
            WebApp: {
                initDataUnsafe: {
                    user: userData
                },
                ready: function() {
                    console.log('Telegram WebApp готов');
                    // Загружаем корзину после готовности WebApp, если функция существует
                    if (userData.id && typeof window.loadCartItems === 'function') {
                        window.loadCartItems();
                    }
                },
                disableClosingConfirmation: function() {
                    console.log('Отключено подтверждение закрытия');
                }
            }
        };
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен');
    
    const cartItemsContainer = document.getElementById('cartItems');
    const cartDropdown = document.querySelector('.cart-dropdown-product');
    const cartIcon = document.querySelector('.cart-icon-product');
    const addToCartButton = document.querySelector('.add_to_cart');

    if (!cartItemsContainer || !cartDropdown || !cartIcon) {
        console.error('Не все необходимые элементы найдены на странице');
        return;
    }

    // Обработчик для кнопки добавления в корзину
    if (addToCartButton) {
        addToCartButton.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            const productId = this.dataset.id;
            console.log('Нажата кнопка добавления в корзину. ID товара:', productId);
            window.addToCart(productId);
        });
    }

    // Обработчик для корзины
    cartIcon.addEventListener('click', () => {
        cartDropdown.classList.toggle('active');
        if (cartDropdown.classList.contains('active') && typeof window.loadCartItems === 'function') {
            window.loadCartItems();
        }
    });

    // Предотвращаем закрытие корзины при клике внутри неё
    cartDropdown.addEventListener('click', (event) => {
        event.stopPropagation();
    });

    // Закрытие корзины при клике вне её
    document.addEventListener('click', (event) => {
        if (!cartDropdown.contains(event.target) && !cartIcon.contains(event.target)) {
            cartDropdown.classList.remove('active');
        }
    });

    // Загружаем корзину только если Telegram WebApp уже инициализирован и функция существует
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe.user.id && typeof window.loadCartItems === 'function') {
        window.loadCartItems();
    }
});