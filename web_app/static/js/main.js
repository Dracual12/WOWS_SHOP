// Логика поиска товаров
const searchInput = document.querySelector('#search-bar');
const searchButton = document.querySelector('#search-button');
const productCards = document.querySelectorAll('.product-card');

if (searchInput && searchButton) {
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.toLowerCase().trim();

        productCards.forEach(card => {
            const productName = card.querySelector('h2').textContent.toLowerCase();

            if (productName.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });

    searchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            searchButton.click();
        }
    });
} else {
    console.error('Поле или кнопка поиска не найдены. Проверьте HTML-код.');
}