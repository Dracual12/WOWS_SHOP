Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();


document.addEventListener('DOMContentLoaded', () => {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartDropdown = document.querySelector('.cart-dropdown');
    const cartIcon = document.querySelector('.cart-icon');

    // При клике по значку корзины переключаем класс "active" и загружаем товары
    cartIcon.addEventListener('click', () => {
        cartDropdown.classList.toggle('active');
        if (cartDropdown.classList.contains('active')) {
            loadCartItems();
        }
    });

    // Функция загрузки товаров корзины
    function loadCartItems() {
        const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;  // Получаем tg_id
        fetch(`/api/cart?tg_id=${tgId}`, {
            method: "GET",  // Используем GET
        })
            .then(response => response.json())
            .then(cartItems => {
                cartItemsContainer.innerHTML = ''; // Очищаем корзину
                if (cartItems.length === 0) {
                    cartItemsContainer.innerHTML = '<li>Корзина пуста</li>';
                } else {
                    cartItems.forEach(item => {
                        const li = document.createElement('li');
                        li.setAttribute('data-product-id', item.id);
                        // Вычисляем цену за единицу: если quantity > 0, то unitPrice = total / quantity, иначе 0
                        const unitPrice = item.quantity > 0 ? parseFloat(item.total) / parseFloat(item.quantity) : 0;
                        li.setAttribute('data-unit-price', unitPrice);
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
                            <span class="item-total">${(unitPrice * item.quantity).toFixed(2)} дублонов</span>
                            </div>
                        `;

                        // Привязываем обработчики для этого элемента
                        const increaseBtn = li.querySelector('.quantity-btn.increase');
                        const decreaseBtn = li.querySelector('.quantity-btn.decrease');
                        const removeBtn = li.querySelector('.remove-btn img');

                        increaseBtn.addEventListener('click', () => {
                            const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                            updateCartQuantity(item.id, currentQuantity + 1, li);
                        });

                        decreaseBtn.addEventListener('click', () => {
                            const currentQuantity = parseInt(li.querySelector('.quantity-value').textContent);
                            if (currentQuantity > 1) {
                                updateCartQuantity(item.id, currentQuantity - 1, li);
                            }
                        });

                        removeBtn.addEventListener('click', () => {
                            removeCartItem(item.id, li);
                        });

                        cartItemsContainer.appendChild(li);
                    });
                }
            })
            .catch(error => console.error('Ошибка загрузки корзины:', error));
    }

    // Функция обновления количества товара
    function updateCartQuantity(productId, newQuantity, li) {
        const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
        fetch(`/api/cart/${productId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: newQuantity, tg: tgId }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка обновления корзины');
                }
                return response.json();
            })
            .then(() => {
                const unitPrice = parseFloat(li.getAttribute('data-unit-price'));
                li.querySelector('.quantity-value').textContent = newQuantity;
                li.querySelector('.item-total').textContent = (unitPrice * newQuantity).toFixed(2) + ' дублонов';
            })
            .catch(error => console.error('Ошибка:', error));
    }

    // Функция удаления товара из корзины
    function removeCartItem(productId, li) {
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
            .then(() => {
                li.remove();
            })
            .catch(error => console.error('Ошибка:', error));
    }
});
