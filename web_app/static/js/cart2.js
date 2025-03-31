console.log('Загрузка cart2.js');

Telegram.WebApp.ready();
console.log('Telegram WebApp готов');

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

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
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
};

// Функция удаления товара из корзины
window.removeCartItem = function(productId, li) {
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    
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
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
};

// Функция оформления заказа
function checkout() {
    console.log('Функция checkout вызвана');
    try {
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
        
        console.log('Перенаправление на форму заказа с ID:', userId);
        window.location.href = `/order?tg_id=${userId}`;
    } catch (error) {
        console.error('Ошибка при оформлении заказа:', error);
    }
}

// Функция для добавления обработчика кнопки оформления заказа
function addCheckoutButtonHandler() {
    const checkoutButton = document.querySelector('.checkout-button');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', function(event) {
            event.stopPropagation();
            checkout();
        });
    }
}

// Функция для обновления корзины
async function updateCart() {
    try {
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

        const response = await fetch(`/api/cart?tg_id=${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        const cartItems = document.getElementById('cart-items-product');
        const cartTotal = document.getElementById('cart-total-product');
        
        if (data && data.length > 0) {
            let total = 0;
            cartItems.innerHTML = data.map(item => {
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                return `
                    <li class="cart-item">
                        <div class="cart-item-top">
                            <span class="item-name">${item.name}</span>
                            <button class="remove-btn" onclick="removeCartItem(${item.product_id}, this.parentElement.parentElement)">
                                <img src="/static/images/delete_good.png" alt="Удалить">
                            </button>
                        </div>
                        <div class="item-quantity">
                            <button class="quantity-btn decrease" onclick="updateCartQuantity(${item.product_id}, ${item.quantity - 1}, this.parentElement.parentElement)">-</button>
                            <span class="quantity-value">${item.quantity}</span>
                            <button class="quantity-btn increase" onclick="updateCartQuantity(${item.product_id}, ${item.quantity + 1}, this.parentElement.parentElement)">+</button>
                        </div>
                        <div class="item-price">
                            <span class="item-total">${itemTotal.toFixed(2)} ₽</span>
                        </div>
                    </li>
                `;
            }).join('');
            
            cartTotal.innerHTML = `
                <div class="total">Итого: ${total.toFixed(2)} ₽</div>
                <button class="checkout-button">Оформить заказ</button>
            `;
            
            // Добавляем обработчик для кнопки оформления заказа
            addCheckoutButtonHandler();
        } else {
            cartItems.innerHTML = '<li class="empty-cart">Корзина пуста</li>';
            cartTotal.innerHTML = '';
        }
    } catch (error) {
        console.error('Ошибка при загрузке корзины:', error);
        const cartItems = document.getElementById('cart-items-product');
        const cartTotal = document.getElementById('cart-total-product');
        cartItems.innerHTML = '<li class="error">Ошибка загрузки</li>';
        cartTotal.innerHTML = '';
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const cartIcon = document.querySelector('.cart-icon-product');
    const cartDropdown = document.querySelector('.cart-dropdown-product');
    
    if (cartIcon && cartDropdown) {
        // Открытие/закрытие корзины
        cartIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            cartDropdown.classList.toggle('show');
            if (cartDropdown.classList.contains('show')) {
                updateCart();
            }
        });

        // Закрытие корзины при клике вне её
        document.addEventListener('click', function(event) {
            if (!cartDropdown.contains(event.target) && event.target !== cartIcon) {
                cartDropdown.classList.remove('show');
            }
        });

        // Загружаем корзину при загрузке страницы
        updateCart();
    }
});

// Функция добавления товара в корзину
async function addToCart(productId, tgId) {
    try {
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                tg_id: tgId,
                quantity: 1
            })
        });
        
        if (response.ok) {
            // Создаем элемент уведомления
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = 'Товар добавлен в корзину';
            document.body.appendChild(notification);

            // Показываем уведомление
            setTimeout(() => notification.classList.add('show'), 100);

            // Скрываем и удаляем уведомление через 3 секунды
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);

            // Обновляем корзину
            updateCart();
        } else {
            console.error('Ошибка при добавлении товара в корзину:', response.status);
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
    }
}