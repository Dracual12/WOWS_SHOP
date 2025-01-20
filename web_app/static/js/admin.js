document.addEventListener("DOMContentLoaded", () => {
    const productTable = document.querySelector("tbody");
    const sectionsTable = document.getElementById("sections-table");
    const addSectionButton = document.getElementById("add-section");
    const addForm = document.querySelector("form");

    // Делегирование событий для товаров
    productTable.addEventListener("click", (event) => {
        const button = event.target;
        const productId = button.getAttribute("data-id");

        if (button.classList.contains("edit-product")) {
            editProduct(productId, button);
        } else if (button.classList.contains("delete-product")) {
            deleteProduct(productId, button);
        }
    });

    // Делегирование событий для секций
    sectionsTable.addEventListener("click", (event) => {
        const button = event.target;
        const sectionId = button.getAttribute("data-id");

        if (button.classList.contains("delete-section")) {
            deleteSection(sectionId, button);
        } else if (button.classList.contains("edit-section")) {
            editSection(sectionId);
        }
    });

    // Добавление товара
    if (addForm) {
        addForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const formData = new FormData(addForm);
            fetch("/admin/add", {
                method: "POST",
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const newProduct = data.product;
                        const newRow = document.createElement("tr");
                        newRow.innerHTML = `
                            <td>${newProduct.id}</td>
                            <td>${newProduct.name}</td>
                            <td>${newProduct.price} дублонов</td>
                            <td>
                                <button class="edit-product" data-id="${newProduct.id}">Редактировать</button>
                                <button class="delete-product" data-id="${newProduct.id}">Удалить</button>
                            </td>
                        `;
                        productTable.appendChild(newRow);
                        alert("Товар успешно добавлен.");
                        addForm.reset();
                    } else {
                        alert("Ошибка добавления товара: " + data.error);
                    }
                })
                .catch(error => alert("Ошибка сервера: " + error.message));
        });
    }

    // Добавление секции
    if (addSectionButton) {
        addSectionButton.addEventListener("click", () => {
            const sectionName = prompt("Введите название секции:");
            if (sectionName) {
                fetch("/admin/add_section", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: sectionName }),
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const newSection = data.section;
                            const newRow = document.createElement("tr");
                            newRow.innerHTML = `
                                <td>${newSection.id}</td>
                                <td>${newSection.name}</td>
                                <td>
                                    <button class="edit-section" data-id="${newSection.id}">Редактировать</button>
                                    <button class="delete-section" data-id="${newSection.id}">Удалить</button>
                                </td>
                            `;
                            sectionsTable.appendChild(newRow);
                            alert("Секция успешно добавлена.");
                        } else {
                            alert("Ошибка добавления секции: " + data.error);
                        }
                    })
                    .catch(error => alert("Ошибка сервера: " + error.message));
            }
        });
    }

    // Редактирование товара
    function editProduct(productId, button) {
        const productRow = button.closest("tr");
        const productName = productRow.querySelector("td:nth-child(2)").textContent;
        const productPrice = productRow.querySelector("td:nth-child(3)").textContent.replace(" дублонов", "");

        const newName = prompt("Введите новое название товара:", productName);
        const newPrice = prompt("Введите новую цену товара:", productPrice);

        if (newName && newPrice) {
            fetch(`/admin/edit/${productId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: newName, price: parseInt(newPrice, 10) }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        productRow.querySelector("td:nth-child(2)").textContent = newName;
                        productRow.querySelector("td:nth-child(3)").textContent = `${newPrice} дублонов`;
                        alert("Товар успешно обновлен.");
                    } else {
                        alert("Ошибка обновления товара: " + data.error);
                    }
                })
                .catch(error => alert("Ошибка сервера: " + error.message));
        }
    }

    // Удаление товара
    function deleteProduct(productId, button) {
        if (confirm("Вы уверены, что хотите удалить этот товар?")) {
            fetch(`/admin/delete/${productId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        button.closest("tr").remove();
                        alert("Товар успешно удален.");
                    } else {
                        alert("Ошибка удаления товара: " + data.error);
                    }
                })
                .catch(error => alert("Ошибка сервера: " + error.message));
        }
    }

    // Редактирование секции
    function editSection(sectionId) {
        const newName = prompt("Введите новое название секции:");
        if (newName) {
            fetch(`/admin/edit_section/${sectionId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: newName }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document
                            .querySelector(`button[data-id="${sectionId}"]`)
                            .closest("tr")
                            .querySelector("td:nth-child(2)").textContent = newName;
                        alert("Секция успешно обновлена.");
                    } else {
                        alert("Ошибка редактирования секции: " + data.error);
                    }
                })
                .catch(error => alert("Ошибка сервера: " + error.message));
        }
    }

    // Удаление секции
    function deleteSection(sectionId, button) {
        if (confirm("Вы уверены, что хотите удалить эту секцию?")) {
            fetch(`/admin/delete_section/${sectionId}`, { method: "DELETE" })
                console.log(sectionId)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        button.closest("tr").remove();
                        alert("Секция успешно удалена.");
                    } else {
                        alert("Ошибка удаления секции: " + data.error);
                    }
                })
                .catch(error => alert("Ошибка сервера: " + error.message));
        }
    }
});
