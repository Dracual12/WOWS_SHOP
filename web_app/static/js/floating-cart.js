// Логика работы плавающей корзины
const floatingCart = document.querySelector('.floating-cart');
const cartContainer = document.createElement('div');
cartContainer.classList.add('cart-container');
document.body.appendChild(cartContainer);

// Содержимое корзины (пример)
let cartItems = [
    { name: '500 дублонов', quantity: 2, price: 500 },
    { name: '1000 дублонов', quantity: 1, price: 950 }
];

// Создание HTML для корзины
function renderCart() {
    cartContainer.innerHTML = '';
    cartContainer.style.display = 'block';

    const closeButton = document.createElement('button');
    closeButton.textContent = 'Закрыть';
    closeButton.classList.add('close-cart');
    closeButton.addEventListener('click', () => {
        cartContainer.style.display = 'none';
    });

    const cartList = document.createElement('ul');
    cartItems.forEach(item => {
        const listItem = document.createElement('li');
        listItem.textContent = `${item.name} x${item.quantity} - ${item.price * item.quantity} дублонов`;
        cartList.appendChild(listItem);
    });

    const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const totalElement = document.createElement('p');
    totalElement.textContent = `Итого: ${total} дублонов`;
    totalElement.classList.add('cart-total');

    cartContainer.appendChild(closeButton);
    cartContainer.appendChild(cartList);
    cartContainer.appendChild(totalElement);
}

// Обработка клика по плавающей корзине
if (floatingCart) {
    floatingCart.addEventListener('click', () => {
        if (cartContainer.style.display === 'block') {
            cartContainer.style.display = 'none';
        } else {
            renderCart();
        }
    });
}

// Стилизация корзины через JavaScript
const style = document.createElement('style');
style.textContent = `
.cart-container {
    position: fixed;
    bottom: 80px;
    right: 20px;
    background: #1e1e1e;
    color: white;
    border: 2px solid #42a5f5;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    display: none;
    max-width: 300px;
    z-index: 1000;
}

.cart-container ul {
    list-style: none;
    padding: 0;
    margin: 0 0 10px;
}

.cart-container ul li {
    margin: 5px 0;
    font-size: 14px;
}

.cart-total {
    font-weight: bold;
    margin-top: 10px;
}

.close-cart {
    background: #42a5f5;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 5px;
    margin-bottom: 10px;
}

.close-cart:hover {
    background: #0d47a1;
}
`;
document.head.appendChild(style);
