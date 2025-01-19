document.addEventListener("DOMContentLoaded", () => {
    // Редактирование товара
    document.querySelectorAll(".edit-product").forEach(button => {
        button.addEventListener("click", () => {
            const productId = button.getAttribute("data-id");
            const productRow = button.closest("tr");
            const productName = productRow.querySelector("td:nth-child(2)").textContent;
            const productPrice = productRow.querySelector("td:nth-child(3)").textContent.replace(" дублонов", "");

            const newName = prompt("Введите новое название товара:", productName);
            const newPrice = prompt("Введите новую цену товара:", productPrice);

            if (newName && newPrice) {
                fetch(`/admin/edit/${productId}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ name: newName, price: parseInt(newPrice, 10) })
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
                });
            }
        });
    });

    // Удаление товара
    document.querySelectorAll(".delete-product").forEach(button => {
        button.addEventListener("click", () => {
            const productId = button.getAttribute("data-id");

            if (confirm("Вы уверены, что хотите удалить этот товар?")) {
                fetch(`/admin/delete/${productId}`, {
                    method: "DELETE"
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        button.closest("tr").remove();
                        alert("Товар успешно удален.");
                    } else {
                        alert("Ошибка удаления товара: " + data.error);
                    }
                });
            }
        });
    });

    // Добавление товара
    const addForm = document.querySelector("form");
    if (addForm) {
        addForm.addEventListener("submit", event => {
            event.preventDefault();

            const formData = new FormData(addForm);

            fetch("/admin/add", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const newProduct = data.product;
                    const tableBody = document.querySelector("tbody");

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
                    tableBody.appendChild(newRow);
                    alert("Товар успешно добавлен.");
                    addForm.reset();
                } else {
                    alert("Ошибка добавления товара: " + data.error);
                }
            });
        });
    }
});
