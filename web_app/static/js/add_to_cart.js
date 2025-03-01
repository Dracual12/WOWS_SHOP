const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(button => {
    button.addEventListener('click', async () => {
        const productId = button.getAttribute('data-id');
        const telegram_id = window.Telegram.WebApp.initDataUnsafe.user.id;

        try {
            const response = await fetch('/api/cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId, quantity: 1, telegram_id: telegram_id }),
            });

            if (!response.ok) {
                const error = await response.json();
                showNotification(`Ошибка: ${error.error}`, 'error'); // Показываем уведомление об ошибке
            } else {
                showNotification('Товар успешно добавлен в корзину!', 'success'); // Показываем уведомление об успехе
            }
        } catch (err) {
            console.error('Ошибка при добавлении в корзину:', err);
            showNotification('Ошибка при добавлении в корзину', 'error'); // Показываем уведомление об ошибке
        }
    });
});

// Функция для показа уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Добавляем уведомление в контейнер
    const container = document.getElementById('notification-container');
    if (!container) {
        // Если контейнера нет, создаем его
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

    // Анимация появления
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300); // Ждем завершения анимации перед удалением
    }, 3000);
}