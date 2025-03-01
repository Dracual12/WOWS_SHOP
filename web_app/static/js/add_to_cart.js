// Функция для обработки добавления в корзину
async function handleAddToCart() {
    const productId = this.getAttribute('data-id');
    const telegram_id = window.Telegram.WebApp.initDataUnsafe.user.id;


    const response = await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity: 1, telegram_id: telegram_id }),
    });
    showNotification('Товар успешно добавлен в корзину!', 'success');
}

// Добавляем обработчики событий
const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(button => {
    button.addEventListener('click', handleAddToCart);
});

// Функция для показа уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    const container = document.getElementById('notification-container');
    if (!container) {
        const newContainer = document.createElement('div');
        newContainer.id = 'notification-container';
        newContainer.style.position = 'fixed';
        newContainer.style.bottom = '20px';
        newContainer.style.right = '20px';
        newContainer.style.zIndex = '1000';
        document.body.appendChild(newContainer);
        container = newContainer;
    }

    container.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}