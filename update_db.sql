-- Добавляем колонку order_index в таблицу sections
ALTER TABLE sections ADD COLUMN order_index INTEGER DEFAULT 0;

-- Добавляем колонку order_index в таблицу products
ALTER TABLE products ADD COLUMN order_index INTEGER DEFAULT 0;

-- Обновляем существующие записи, устанавливая order_index
UPDATE sections SET order_index = id;
UPDATE products SET order_index = id;

-- Переименовываем колонку user_id в tg_id в таблице cart
ALTER TABLE cart RENAME COLUMN user_id TO tg_id; 