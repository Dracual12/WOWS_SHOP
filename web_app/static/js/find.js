Telegram.WebApp.ready();

// Отключаем возможность закрытия жестом "pull-to-close"
Telegram.WebApp.disableClosingConfirmation();

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-bar");
  function blurIfOutside(event) {
    if (searchInput === document.activeElement && !event.target.closest('#search-bar')) {
      searchInput.blur();
    }
  }

  document.addEventListener('click', blurIfOutside);
  document.addEventListener('touchend', blurIfOutside);

    function setupSearch() {
        const productSections = document.querySelectorAll(".section");

        searchInput.addEventListener("input", () => {
            const query = searchInput.value.toLowerCase();

            productSections.forEach(section => {
                let hasVisibleProducts = false;
                const products = section.querySelectorAll(".carousel-item");

                products.forEach(product => {
                    const productName = product.querySelector("h3").textContent.toLowerCase();
                    if (productName.includes(query)) {
                        product.style.display = "block";
                        hasVisibleProducts = true;
                    } else {
                        product.style.display = "none";
                    }
                });

                // Если в секции нет подходящих товаров — скрываем её
                section.style.display = hasVisibleProducts ? "block" : "none";
            });
        });
    }

    // Ожидаем загрузки товаров перед активацией поиска
    function waitForProducts() {
        const checkExist = setInterval(() => {
            if (document.querySelector(".carousel-item")) {
                clearInterval(checkExist);
                setupSearch();
            }
        }, 100); // Проверяем каждые 100мс
    }

    waitForProducts();
});
