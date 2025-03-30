document.addEventListener('DOMContentLoaded', function() {
    // Получаем все поля ввода
    const inputs = document.querySelectorAll('.form-group input');
    
    // Добавляем обработчик клика на документ
    document.addEventListener('click', function(event) {
        // Проверяем, был ли клик вне поля ввода
        if (!event.target.matches('.form-group input')) {
            // Скрываем клавиатуру, убирая фокус с активного поля
            document.activeElement.blur();
        }
    });

    // Предотвращаем всплытие события клика при нажатии на поля ввода
    inputs.forEach(input => {
        input.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
}); 