const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(button => {
    button.addEventListener('click', async () => {
        const productId = button.getAttribute('data-id');
        const telegram_id = window.Telegram.WebApp.initDataUnsafe.user.id;
        try {
            const response = await fetch('/api/cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({product_id: productId, quantity: 1, telegram_id: telegram_id}),
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Ошибка: ${error.error}`);
            } else {
                // Вместо alert, показываем всплывающее окно
                showAddedPopup();
            }
        } catch (err) {
            console.error('Ошибка при добавлении в корзину:', err);
        }
    });
    function showAddedPopup() {
    const popup = document.createElement('div');
    popup.classList.add('popup-message');
    popup.innerHTML = `
        <button class="close-btn"><img src="/static/images/crest.png" alt="Закрыть"></button>
        <p>Товар успешно добавлен в корзину!</p>
    `;
    document.body.appendChild(popup);

    // Обработчик для закрытия окна
    popup.querySelector('.close-btn').addEventListener('click', () => {
        popup.remove();
    });

    // Автоматическое скрытие через 3 секунды (по желанию)
    setTimeout(() => {
        if (popup.parentNode) {
            popup.remove();
        }
    }, 3000);
}

});
