Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

document.addEventListener("DOMContentLoaded", () => {
    const sectionsContainer = document.getElementById("sections-container");

    // Загружаем секции и товары
    fetch('/api/sections')
        .then(response => response.json())
        .then(sections => {
            console.log('Получены секции:', sections);
            Object.values(sections).forEach(section => {
                // Создаём секцию
                const sectionElement = document.createElement("div");
                sectionElement.classList.add("section");
                sectionElement.innerHTML = `
                    <h2>${section.section_name}</h2>
                    <div class="product-carousel">
                        ${section.products.map(product => `
                            <div class="carousel-item" data-product-id="${product.id}">
                                <img src="${product.image}" alt="${product.name}" class="carousel-image">
                                <h3>${product.name}</h3>
                                <p>${product.price} рублей</p>
                            </div>
                        `).join("")}
                    </div>
                `;
                sectionsContainer.appendChild(sectionElement);
            });

            // Добавляем обработчики для открытия страницы товара
            document.querySelectorAll('.carousel-item').forEach(item => {
                item.addEventListener('click', () => {
                    const productId = item.dataset.productId;
                    if (productId) {
                        window.location.href = `/product/${productId}`;
                    } else {
                        console.error('ID товара не найден');
                    }
                });
            });
        })
        .catch(error => {
            console.error('Ошибка загрузки секций:', error);
            sectionsContainer.innerHTML = '<p class="error">Ошибка загрузки данных. Пожалуйста, обновите страницу.</p>';
        });
});
