document.addEventListener('DOMContentLoaded', () => {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartDropdown = document.querySelector('.cart-dropdown');
    const cartIcon = document.querySelector('.cart-icon');

    // Загружаем товары корзины при открытии
    cartIcon.addEventListener('click', () => {
        cartDropdown.classList.toggle('hidden');
        if (!cartDropdown.classList.contains('hidden')) {
            loadCartItems();
        }
    });

    // Загружаем товары корзины
    function loadCartItems() {
        fetch('/api/cart')
            .then(response => response.json())
            .then(cartItems => {
                cartItemsContainer.innerHTML = ''; // Очищаем корзину
                if (cartItems.length === 0) {
                    cartItemsContainer.innerHTML = '<li>Корзина пуста</li>';
                } else {
                    cartItems.forEach(item => {
                        const cartItem = `
                            <li data-product-id="${item.product_id}">
                                <span class="item-name">${item.name}</span>
                                <span class="item-quantity">
                                    <button class="quantity-btn decrease">-</button>
                                    <span class="quantity-value">${item.quantity}</span>
                                    <button class="quantity-btn increase">+</button>
                                </span>
                                <span class="item-total">${item.total} дублонов</span>
                                <button class="remove-btn">Удалить</button>
                            </li>`;
                        cartItemsContainer.innerHTML += cartItem;
                    });
                }
            })
            .catch(error => console.error('Ошибка загрузки корзины:', error));
    }

    // Обработка нажатий в корзине
    cartItemsContainer.addEventListener('click', (event) => {
        const button = event.target;
        const listItem = button.closest('li');
        const productId = listItem.getAttribute('data-product-id');
        const quantityElement = listItem.querySelector('.quantity-value');

        if (button.classList.contains('increase')) {
            // Увеличить количество
            let quantity = parseInt(quantityElement.textContent);
            quantity += 1;
            updateCartQuantity(productId, quantity);
        } else if (button.classList.contains('decrease')) {
            // Уменьшить количество
            let quantity = parseInt(quantityElement.textContent);
            if (quantity > 1) {
                quantity -= 1;
                updateCartQuantity(productId, quantity);
            }
        } else if (button.classList.contains('remove-btn')) {
            // Удалить товар из корзины
            removeCartItem(productId);
        }
    });

    // Обновить количество товара
    function updateCartQuantity(productId, quantity) {
        fetch(`/api/cart/${productId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: quantity }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка обновления корзины');
                }
                return response.json();
            })
            .then(() => {
                loadCartItems(); // Обновляем корзину
            })
            .catch(error => console.error('Ошибка:', error));
    }

    // Удалить товар из корзины
    function removeCartItem(productId) {
        fetch(`/api/cart/${productId}`, {
            method: 'DELETE',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка удаления товара из корзины');
                }
                return response.json();
            })
            .then(() => {
                loadCartItems(); // Обновляем корзину
            })
            .catch(error => console.error('Ошибка:', error));
    }
});
