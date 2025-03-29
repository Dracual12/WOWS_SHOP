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

// Функция обновления количества товара
window.updateCartQuantity = function(productId, newQuantity, li) {
    if (newQuantity < 1) {
        // Если количество меньше 1, удаляем товар
        window.removeCartItem(productId, li);
        return;
    }

    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    
    // Сначала обновляем UI
    updateItemUI(li, newQuantity);
    
    console.log('Отправка запроса на обновление количества:', {
        productId,
        newQuantity,
        tgId
    });
    
    fetch(`/api/cart/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity, tg_id: tgId })
    })
    .then(response => {
        if (!response.ok) {
            // В случае ошибки откатываем изменения
            updateItemUI(li, newQuantity - 1);
            throw new Error('Ошибка обновления корзины');
        }
        return response.json();
    })
    .then(data => {
        if (data.status !== 'success') {
            // В случае ошибки откатываем изменения
            updateItemUI(li, newQuantity - 1);
            console.error('Ошибка обновления:', data);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
};

// Функция локального обновления UI элемента корзины
function updateItemUI(li, quantity) {
    const quantityElement = li.querySelector('.quantity-value');
    const priceElement = li.querySelector('.cart-item-price');
    const price = parseFloat(priceElement.textContent.replace(/[^0-9.]/g, ''));
    const productId = li.dataset.productId;
    
    // Обновляем количество
    quantityElement.textContent = quantity;
    
    // Обновляем кнопки с новым значением количества
    const minusButton = li.querySelector('.cart-item-quantity button:first-child');
    const plusButton = li.querySelector('.cart-item-quantity button:last-child');
    
    // Удаляем старые обработчики
    minusButton.replaceWith(minusButton.cloneNode(true));
    plusButton.replaceWith(plusButton.cloneNode(true));
    
    // Получаем новые кнопки после замены
    const newMinusButton = li.querySelector('.cart-item-quantity button:first-child');
    const newPlusButton = li.querySelector('.cart-item-quantity button:last-child');
    
    // Добавляем новые обработчики
    newMinusButton.addEventListener('click', () => {
        updateCartQuantity(productId, quantity - 1, li);
    });
    
    newPlusButton.addEventListener('click', () => {
        updateCartQuantity(productId, quantity + 1, li);
    });
    
    // Обновляем общую сумму
    updateTotalSum();
}

// Функция обновления общей суммы
function updateTotalSum() {
    const cartItems = document.querySelectorAll('.cart-item');
    let totalSum = 0;
    
    cartItems.forEach(item => {
        // Извлекаем только числовое значение цены
        const priceText = item.querySelector('.cart-item-price').textContent;
        const price = parseFloat(priceText.replace(/[^0-9.]/g, ''));
        const quantity = parseInt(item.querySelector('.quantity-value').textContent);
        
        console.log('Подсчет суммы:', { price, quantity, total: price * quantity });
        
        if (!isNaN(price) && !isNaN(quantity)) {
            totalSum += price * quantity;
        }
    });
    
    const totalElement = document.querySelector('.total-sum');
    if (totalElement) {
        totalElement.textContent = `Итого: ${totalSum.toFixed(2)} ₽`;
    }
    
    console.log('Общая сумма:', totalSum);
}

// Функция удаления товара из корзины
window.removeCartItem = function(productId, li) {
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    console.log('Отправка запроса на удаление:', {
        productId,
        tgId
    });
    
    fetch(`/api/cart/${tgId}/${productId}`, {
        method: 'DELETE',
    })
        .then(response => {
            console.log('Получен ответ:', response.status);
            if (!response.ok) {
                throw new Error('Ошибка удаления товара из корзины');
            }
            return response.json();
        })
        .then(data => {
            console.log('Данные ответа:', data);
            if (data.status === 'success') {
                // Перезагружаем корзину для обновления общей суммы
                window.loadCartItems();
            } else {
                console.error('Ошибка удаления:', data);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
};

// Функция для загрузки товаров в корзину
window.loadCartItems = function() {
    fetch('/api/cart')
        .then(response => response.json())
        .then(data => {
            console.log('Данные корзины:', data);
            const cartItems = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');
            const cartIcon = document.querySelector('.cart-icon-product') || document.querySelector('.cart-icon');
            const cartDropdown = document.querySelector('.cart-dropdown-product') || document.querySelector('.cart-dropdown');

            if (!cartItems || !cartTotal) {
                console.error('Элементы корзины не найдены');
                return;
            }

            cartItems.innerHTML = '';
            let total = 0;

            if (data && data.items && data.items.length > 0) {
                console.log('Товары в корзине:', data.items);
                data.items.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'cart-item';
                    li.innerHTML = `
                        <div class="cart-item-details">
                            <div class="cart-item-top">
                                <span class="cart-item-name">${item.name}</span>
                                <span class="cart-item-price">${item.price} ₽</span>
                            </div>
                            <div class="cart-item-bottom">
                                <div class="cart-item-quantity">
                                    <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">-</button>
                                    <span>${item.quantity}</span>
                                    <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
                                </div>
                                <button class="remove-item" onclick="removeFromCart(${item.id})">×</button>
                            </div>
                        </div>
                    `;
                    cartItems.appendChild(li);
                    total += item.price * item.quantity;
                });

                cartTotal.innerHTML = `
                    <div class="total-sum">Итого: ${total} ₽</div>
                    <button class="checkout-button" onclick="checkout()">Оформить заказ</button>
                `;
            } else {
                console.log('Корзина пуста или нет данных:', data);
                cartItems.innerHTML = '<li class="empty-cart">Корзина пуста</li>';
                cartTotal.innerHTML = '';
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке корзины:', error);
            const cartItems = document.getElementById('cartItems');
            if (cartItems) {
                cartItems.innerHTML = '<li class="empty-cart">Ошибка загрузки корзины</li>';
            }
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
