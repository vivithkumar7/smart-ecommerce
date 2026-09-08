CREATE TABLE IF NOT EXISTS product_views (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    user_id INT NULL,
    viewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_product_views_product_id (product_id),
    INDEX ix_product_views_user_id (user_id),
    INDEX ix_product_views_viewed_at (viewed_at),
    CONSTRAINT fk_product_views_product FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT fk_product_views_user FOREIGN KEY (user_id) REFERENCES users (id)
);