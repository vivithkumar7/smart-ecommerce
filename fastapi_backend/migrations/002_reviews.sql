CREATE TABLE IF NOT EXISTS reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    rating INT NOT NULL,
    comment TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_review_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT check_review_status CHECK (status IN ('pending', 'approved', 'rejected')),
    CONSTRAINT uq_review_user_product UNIQUE (user_id, product_id),
    INDEX ix_reviews_user_id (user_id),
    INDEX ix_reviews_product_id (product_id),
    CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES products (id)
);