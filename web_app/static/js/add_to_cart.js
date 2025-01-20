const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(button => {
    button.addEventListener('click', async () => {
        const productId = button.getAttribute('data-id');
        const userTelegramId = 1456241115
        if (!userTelegramId) {
            alert('Ошибка: Telegram ID не найден!');
            return;
        }
        try {
            const response = await fetch('/api/cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userTelegramId: userTelegramId, product_id: productId, quantity: 1 }),
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Ошибка: ${error.error}`);
            } else {
                alert('Товар добавлен в корзину!');
            }
        } catch (err) {
            console.error('Ошибка при добавлении в корзину:', err);
        }
    });
});
