console.log('Загрузка cart2.js');

Telegram.WebApp.ready();
console.log('Telegram WebApp готов');

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

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

// Делаем функцию доступной глобально
window.loadCartItems = function() {
    console.log('Загрузка товаров корзины');
    const cartItemsContainer = document.getElementById('cart-items-product');
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;  // Получаем tg_id
    console.log('TG ID:', tgId);
    
    fetch(`/api/cart?tg_id=${tgId}`, {
        method: "GET",  // Используем GET
    })
        .then(response => response.json())
        .then(cartItems => {
            console.log('Получены товары:', cartItems);
            cartItemsContainer.innerHTML = ''; // Очищаем корзину
            let totalSum = 0; // Общая сумма корзины
            
            if (cartItems.length === 0) {
                cartItemsContainer.innerHTML = '<li>Корзина пуста</li>';
            } else {
                cartItems.forEach(item => {
                    console.log('Создание элемента корзины для товара:', item);
                    const li = document.createElement('li');
                    
                    // Проверяем наличие product_id в item
                    if (!item.product_id) {
                        console.error('У товара отсутствует product_id:', item);
                        return;
                    }
                    
                    li.setAttribute('data-product-id', item.product_id);
                    
                    // Используем цену из базы данных напрямую
                    const unitPrice = parseFloat(item.price);
                    if (isNaN(unitPrice)) {
                        console.error('Некорректная цена для товара:', item);
                        return;
                    }
                    
                    li.setAttribute('data-unit-price', unitPrice);
                    const itemTotal = unitPrice * parseInt(item.quantity);
                    totalSum += itemTotal; // Добавляем к общей сумме
                    
                    console.log('Созданный элемент li:', {
                        'data-product-id': li.getAttribute('data-product-id'),
                        'data-unit-price': li.getAttribute('data-unit-price'),
                        itemTotal
                    });

                    li.innerHTML = `
                        <div class="cart-item-top">
                            <span class="item-name">${item.name}</span>
                            <button class="remove-btn">
                                <img src="/static/images/delete_good.png" alt="Удалить">
                            </button>
                        </div>
                        <div class="item-quantity">
                            <button class="quantity-btn decrease">-</button>
                            <span class="quantity-value">${item.quantity}</span>
                            <button class="quantity-btn increase">+</button>
                        </div>
                        <div class='item-price'>
                            <span class="item-total">${itemTotal.toFixed(2)} рублей</span>
                        </div>
                    `;

                    // Привязываем обработчики для этого элемента
                    const increaseBtn = li.querySelector('.quantity-btn.increase');
                    const decreaseBtn = li.querySelector('.quantity-btn.decrease');
                    const removeBtn = li.querySelector('.remove-btn');

                    console.log('Найдены кнопки для товара', item.product_id, ':', {
                        increase: !!increaseBtn,
                        decrease: !!decreaseBtn,
                        remove: !!removeBtn
                    });

                    if (increaseBtn) {
                        increaseBtn.addEventListener('click', (e) => {
                            console.log('Нажата кнопка увеличения количества для товара', item.product_id);
                            e.preventDefault();
                            e.stopPropagation();
                            const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                            window.updateCartQuantity(item.product_id, currentQuantity + 1, li);
                        });
                    }

                    if (decreaseBtn) {
                        decreaseBtn.addEventListener('click', (e) => {
                            console.log('Нажата кнопка уменьшения количества для товара', item.product_id);
                            e.preventDefault();
                            e.stopPropagation();
                            const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                            if (currentQuantity > 1) {
                                window.updateCartQuantity(item.product_id, currentQuantity - 1, li);
                            }
                        });
                    }

                    if (removeBtn) {
                        removeBtn.addEventListener('click', (e) => {
                            console.log('Нажата кнопка удаления для товара', item.product_id);
                            e.preventDefault();
                            e.stopPropagation();
                            window.removeCartItem(item.product_id, li);
                        });
                    }

                    cartItemsContainer.appendChild(li);
                });
                
                // Добавляем общую сумму и кнопку оформления заказа
                const totalElement = document.createElement('li');
                totalElement.className = 'cart-total';
                totalElement.innerHTML = `
                    <div class="total-sum">Итого: ${totalSum.toFixed(2)} рублей</div>
                    <button class="checkout-button">Оформить заказ</button>
                `;
                cartItemsContainer.appendChild(totalElement);

                // Добавляем обработчик для кнопки оформления заказа
                const checkoutButton = totalElement.querySelector('.checkout-button');
                if (checkoutButton) {
                    checkoutButton.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        checkout();
                    });
                }
            }
        })
        .catch(error => console.error('Ошибка загрузки корзины:', error));
};

// Функция оформления заказа
function checkout() {
    const tg = window.Telegram.WebApp;
    const userId = tg.initDataUnsafe.user.id;
    window.location.href = `/order_form?tg_id=${userId}`;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен');
    
    const cartItemsContainer = document.getElementById('cart-items-product');
    const cartDropdown = document.querySelector('.cart-dropdown-product');
    const cartIcon = document.querySelector('.cart-icon-product');

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