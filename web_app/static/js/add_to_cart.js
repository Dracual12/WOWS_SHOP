let isHandlerAdded = false; // Флаг для проверки

function setupAddToCartButtons() {
    if (isHandlerAdded) return; // Если обработчик уже добавлен, выходим

    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });

    isHandlerAdded = true; // Устанавливаем флаг
}

// Вызываем функцию для настройки кнопок
setupAddToCartButtons();

async function handleAddToCart() {
    console.log('Кнопка нажата'); // Лог для отладки

    const productId = this.getAttribute('data-product-id');
    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;

    try {
        console.log('Отправка запроса на сервер'); // Лог для отладки
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                tg_id: tgId
            })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            console.log('Товар успешно добавлен'); // Лог для отладки
            showNotification('Товар успешно добавлен в корзину!', 'success');
            
            // Обновляем корзину, если она открыта
            const cartDropdown = document.querySelector('.cart-dropdown-product');
            if (cartDropdown && cartDropdown.classList.contains('active')) {
                loadCartItems();
            }
        } else {
            console.log('Ошибка:', data); // Лог для отладки
            showNotification(data.message || 'Ошибка при добавлении товара', 'error');
        }
    } catch (err) {
        console.error('Ошибка при добавлении в корзину:', err);
        showNotification('Ошибка при добавлении в корзину', 'error');
    }
}

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