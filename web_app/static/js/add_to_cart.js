let isHandlerAdded = false; // Флаг для проверки

function setupAddToCartButtons() {
    if (isHandlerAdded) return; // Если обработчик уже добавлен, выходим

    const addToCartButtons = document.querySelectorAll('.add_to_cart');
    console.log('Найдено кнопок:', addToCartButtons.length); // Лог для отладки
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });

    isHandlerAdded = true; // Устанавливаем флаг
}

// Вызываем функцию для настройки кнопок при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    setupAddToCartButtons();
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

// Функция добавления товара в корзину
async function handleAddToCart() {
    console.log('Кнопка нажата'); // Лог для отладки

    const productId = this.getAttribute('data-id');
    if (!productId) {
        console.error('Не удалось получить ID товара');
        showNotification('Ошибка: не удалось получить ID товара', 'error');
        return;
    }

    const tgId = window.Telegram.WebApp.initDataUnsafe.user.id;
    if (!tgId) {
        console.error('Не удалось получить ID пользователя Telegram');
        showNotification('Ошибка: не удалось получить ID пользователя', 'error');
        return;
    }
    
    console.log('Product ID:', productId);
    console.log('TG ID:', tgId);

    try {
        console.log('Отправка запроса на сервер');
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                tg_id: tgId,
                quantity: 1
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Ответ сервера:', data);
        
        if (data.status === 'success') {
            console.log('Товар успешно добавлен');
            showNotification('Товар успешно добавлен в корзину!', 'success');
            
            // Обновляем корзину, если она открыта
            const cartDropdown = document.querySelector('.cart-dropdown-product');
            if (cartDropdown && cartDropdown.classList.contains('active')) {
                if (typeof window.loadCartItems === 'function') {
                    window.loadCartItems();
                }
            }
        } else {
            console.error('Ошибка при добавлении товара:', data.message);
            showNotification(data.message || 'Ошибка при добавлении товара в корзину', 'error');
        }
    } catch (error) {
        console.error('Ошибка при добавлении товара:', error);
        showNotification('Ошибка при добавлении товара в корзину', 'error');
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.disableClosingConfirmation();
    }

    // Настройка кнопок добавления в корзину
    const addToCartButtons = document.querySelectorAll('.add_to_cart');
    console.log('Найдено кнопок:', addToCartButtons.length);
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });
});