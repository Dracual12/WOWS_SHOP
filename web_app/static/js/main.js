document.addEventListener("DOMContentLoaded", () => {
    const sectionsContainer = document.getElementById("sections-container");

    // Загружаем секции и товары
    fetch('/api/sections')
        .then(response => response.json())
        .then(sections => {
            console.log(sections)
            Object.values(sections).forEach(section => {
                // Создаём секцию
                const sectionElement = document.createElement("div");
                sectionElement.classList.add("section");
                sectionElement.innerHTML = `
                    <h2>${section.section_name}</h2>
                    <div class="product-carousel">
                        ${section.products.map(product => `
                            <div class="carousel-item">
                                <img src="${product.image}" alt="${product.name}" class="carousel-image">
                                <h3>${product.name}</h3>
                                <p>${product.price} дублонов</p>
                            </div>
                        `).join("")}
                    </div>
                `;
                sectionsContainer.appendChild(sectionElement);
            });

            // Добавляем обработчики для открытия страницы товара
            document.querySelectorAll('.carousel-item').forEach(item => {
                item.addEventListener('click', () => {
                    const productName = item.querySelector('h3').textContent;
                    fetch('/api/products')
                        .then(response => response.json())
                        .then(products => {
                            const product = products.find(p => p.name === productName);
                            if (product) {
                                window.location.href = `/product/${product.id}`;
                            }
                        });
                });
            });
        })
        .catch(error => console.error('Ошибка загрузки секций:', error));
});
