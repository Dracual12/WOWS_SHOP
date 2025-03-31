console.log('Загрузка cart.js');

Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();


document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен');
    
    const cartItemsContainer = document.getElementById('cartItems');
    const cartDropdown = document.querySelector('.cart-dropdown');
    const cartIcon = document.querySelector('.cart-icon');

    console.log('Найдены элементы:', {
        cartItemsContainer: !!cartItemsContainer,
        cartDropdown: !!cartDropdown,
        cartIcon: !!cartIcon
    });

    if (!cartItemsContainer || !cartDropdown || !cartIcon) {
        console.error('Не все необходимые элементы найдены на странице');
        return;
    }

    // При клике по значку корзины переключаем класс "active" и загружаем товары
    cartIcon.addEventListener('click', () => {
        console.log('Клик по иконке корзины');
        cartDropdown.classList.toggle('active');
        if (cartDropdown.classList.contains('active')) {
            console.log('Корзина открыта, загружаем товары');
            window.loadCartItems();
        } else {
            console.log('Корзина закрыта');
        }
    });
});

// Функция загрузки корзины
window.loadCartItems = function() {
    const tg = window.Telegram.WebApp;
    if (!tg) {
        console.error('Telegram WebApp не инициализирован');
        return;
    }
    
    const userId = tg.initDataUnsafe.user.id;
    if (!userId) {
        console.error('Не удалось получить ID пользователя');
        return;
    }

    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    
    if (!cartItemsContainer || !cartTotalElement) {
        console.error('Не найдены элементы корзины');
        return;
    }

    fetch(`/api/cart?tg_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            cartItemsContainer.innerHTML = '';
            let totalSum = 0;

            data.forEach(item => {
                const li = document.createElement('li');
                li.className = 'cart-item';
                li.innerHTML = `
                    <div class="cart-item-details">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-price">${item.price} ₽ × ${item.quantity}</div>
                    </div>
                    <div class="cart-item-controls">
                        <button class="quantity-btn minus" data-product-id="${item.product_id}">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn plus" data-product-id="${item.product_id}">+</button>
                        <button class="remove-btn" data-product-id="${item.product_id}">×</button>
                    </div>
                `;

                // Добавляем обработчики для кнопок
                const minusBtn = li.querySelector('.minus');
                const plusBtn = li.querySelector('.plus');
                const removeBtn = li.querySelector('.remove-btn');

                if (minusBtn && plusBtn) {
                    minusBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        if (item.quantity > 1) {
                            window.updateCartQuantity(item.product_id, item.quantity - 1);
                        }
                    });

                    plusBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        window.updateCartQuantity(item.product_id, item.quantity + 1);
                    });
                }

                if (removeBtn) {
                    removeBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        window.removeFromCart(item.product_id);
                    });
                }

                cartItemsContainer.appendChild(li);
                totalSum += item.price * item.quantity;
            });

            cartTotalElement.innerHTML = `
                <div class="total-sum">Итого: ${totalSum.toFixed(2)} ₽</div>
            `;
        })
        .catch(error => {
            console.error('Ошибка при загрузке корзины:', error);
            cartItemsContainer.innerHTML = '<li class="empty-cart">Ошибка загрузки корзины</li>';
        });
};

// Функция обновления количества товара
window.updateCartQuantity = function(productId, quantity) {
    const tg = window.Telegram.WebApp;
    if (!tg) return;
    
    const userId = tg.initDataUnsafe.user.id;
    if (!userId) return;

    fetch('/api/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            tg_id: userId
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            window.loadCartItems();
        }
    })
    .catch(error => console.error('Ошибка обновления количества:', error));
};

// Функция удаления товара из корзины
window.removeFromCart = function(productId) {
    const tg = window.Telegram.WebApp;
    if (!tg) return;
    
    const userId = tg.initDataUnsafe.user.id;
    if (!userId) return;

    fetch('/api/cart/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            tg_id: userId
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            window.loadCartItems();
        }
    })
    .catch(error => console.error('Ошибка удаления товара:', error));
};

// Функция оформления заказа
window.checkout = function() {
    const tg = window.Telegram.WebApp;
    if (!tg) {
        console.error('Telegram WebApp не инициализирован');
        return;
    }
    
    const userId = tg.initDataUnsafe.user.id;
    if (!userId) {
        console.error('Не удалось получить ID пользователя');
        return;
    }
    
    window.location.href = `/order?tg_id=${userId}`;
};
