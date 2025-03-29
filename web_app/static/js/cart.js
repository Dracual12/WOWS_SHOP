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
    // Получаем productId из data-атрибута элемента, если он не передан
    if (!productId && li) {
        productId = li.getAttribute('data-product-id');
    }
    
    if (!productId) {
        console.error('Не удалось получить ID товара');
        console.log('Элемент li:', li);
        console.log('data-product-id:', li ? li.getAttribute('data-product-id') : 'нет элемента');
        return;
    }

    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    console.log('Отправка запроса на обновление количества:', {
        productId,
        newQuantity,
        tgId,
        li: li ? {
            'data-product-id': li.getAttribute('data-product-id'),
            'data-unit-price': li.getAttribute('data-unit-price')
        } : 'нет элемента'
    });
    
    fetch(`/api/cart/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity, tg_id: tgId }),
    })
        .then(response => {
            console.log('Получен ответ:', response.status);
            if (!response.ok) {
                throw new Error('Ошибка обновления корзины');
            }
            return response.json();
        })
        .then(data => {
            console.log('Данные ответа:', data);
            if (data.status === 'success') {
                const unitPrice = parseFloat(li.getAttribute('data-unit-price'));
                li.querySelector('.quantity-value').textContent = newQuantity;
                li.querySelector('.item-total').textContent = (unitPrice * newQuantity).toFixed(2) + ' рублей';
                // Перезагружаем корзину для обновления общей суммы
                window.loadCartItems();
            } else {
                console.error('Ошибка обновления:', data);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
};

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

// Функция загрузки товаров корзины
window.loadCartItems = function() {
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotalElement = document.getElementById('cartTotal');
    
    // Получаем товары из localStorage
    const cartItems = JSON.parse(localStorage.getItem('cartItems')) || [];
    
    // Очищаем контейнер
    cartItemsContainer.innerHTML = '';
    
    if (cartItems.length === 0) {
        // Если корзина пуста
        cartItemsContainer.innerHTML = '<li class="empty-cart">Корзина пуста</li>';
        cartTotalElement.innerHTML = '';
        return;
    }
    
    let totalSum = 0;
    
    // Добавляем каждый товар
    cartItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'cart-item';
        li.innerHTML = `
            <img src="${item.image}" alt="${item.name}" class="cart-item-image">
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price} ₽</div>
                <div class="cart-item-quantity">
                    <button onclick="updateQuantity(${item.id}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateQuantity(${item.id}, 1)">+</button>
                </div>
            </div>
            <button onclick="removeFromCart(${item.id})" class="remove-item">×</button>
        `;
        cartItemsContainer.appendChild(li);
        totalSum += item.price * item.quantity;
    });
    
    // Обновляем общую сумму и добавляем кнопку оформления заказа
    cartTotalElement.innerHTML = `
        <div class="total-sum">Итого: ${totalSum.toFixed(2)} ₽</div>
        <button class="checkout-button">Оформить заказ</button>
    `;
    
    // Добавляем обработчик для кнопки оформления заказа
    const checkoutButton = cartTotalElement.querySelector('.checkout-button');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            checkout();
        });
    }
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
