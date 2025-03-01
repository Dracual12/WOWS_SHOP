// Функция для обработки добавления в корзину
async function handleAddToCart() {
    const productId = this.getAttribute('data-id');
    const telegram_id = window.Telegram.WebApp.initDataUnsafe.user.id;

    try {
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1, telegram_id: telegram_id }),
        });

        if (!response.ok) {
            const error = await response.json();
            showNotification(`Ошибка: ${error.error}`, 'error');
        } else {
            showNotification('Товар успешно добавлен в корзину!', 'success');
        }
    } catch (err) {
        console.error('Ошибка при добавлении в корзину:', err);
        showNotification('Ошибка при добавлении в корзину', 'error');
    }
}

// Добавляем обработчики событий
const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(button => {
    // Удаляем старые обработчики (если они есть)
    button.removeEventListener('click', handleAddToCart);
    // Добавляем новый обработчик
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