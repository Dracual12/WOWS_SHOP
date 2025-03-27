Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

// Функция обновления количества товара
window.updateCartQuantity = function(productId, newQuantity, li) {
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
    const cartItemsContainer = document.getElementById('cart-items-product');
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;  // Получаем tg_id
    fetch(`/api/cart?tg_id=${tgId}`, {
        method: "GET",  // Используем GET
    })
        .then(response => response.json())
        .then(cartItems => {
            cartItemsContainer.innerHTML = ''; // Очищаем корзину
            let totalSum = 0; // Общая сумма корзины
            
            if (cartItems.length === 0) {
                cartItemsContainer.innerHTML = '<li>Корзина пуста</li>';
            } else {
                cartItems.forEach(item => {
                    const li = document.createElement('li');
                    li.setAttribute('data-product-id', item.id);
                    
                    // Используем цену из базы данных напрямую
                    const unitPrice = parseFloat(item.price);
                    li.setAttribute('data-unit-price', unitPrice);
                    const itemTotal = unitPrice * parseInt(item.quantity);
                    totalSum += itemTotal; // Добавляем к общей сумме
                    
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

                    console.log('Найдены кнопки:', {
                        increase: increaseBtn,
                        decrease: decreaseBtn,
                        remove: removeBtn
                    });

                    increaseBtn.addEventListener('click', () => {
                        console.log('Нажата кнопка увеличения количества');
                        const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                        window.updateCartQuantity(item.id, currentQuantity + 1, li);
                    });

                    decreaseBtn.addEventListener('click', () => {
                        console.log('Нажата кнопка уменьшения количества');
                        const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                        if (currentQuantity > 1) {
                            window.updateCartQuantity(item.id, currentQuantity - 1, li);
                        }
                    });

                    removeBtn.addEventListener('click', () => {
                        console.log('Нажата кнопка удаления');
                        window.removeCartItem(item.id, li);
                    });

                    cartItemsContainer.appendChild(li);
                });
                
                // Добавляем общую сумму в конец корзины
                const totalElement = document.createElement('li');
                totalElement.className = 'cart-total';
                totalElement.innerHTML = `<div class="total-sum">Итого: ${totalSum.toFixed(2)} рублей</div>`;
                cartItemsContainer.appendChild(totalElement);
            }
        })
        .catch(error => console.error('Ошибка загрузки корзины:', error));
};

document.addEventListener('DOMContentLoaded', () => {
    const cartItemsContainer = document.getElementById('cart-items-product');
    const cartDropdown = document.querySelector('.cart-dropdown-product');
    const cartIcon = document.querySelector('.cart-icon-product');

    // При клике по значку корзины переключаем класс "active" и загружаем товары
    cartIcon.addEventListener('click', () => {
        cartDropdown.classList.toggle('active');
        if (cartDropdown.classList.contains('active')) {
            window.loadCartItems();
        }
    });
});