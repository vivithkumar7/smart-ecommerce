CREATE TABLE IF NOT EXISTS blog_posts (
    id INT NOT NULL AUTO_INCREMENT,
    author_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL,
    excerpt VARCHAR(500) NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_blog_posts_slug (slug),
    KEY ix_blog_posts_author_id (author_id),
    KEY ix_blog_posts_category (category),
    KEY ix_blog_posts_status (status),
    CONSTRAINT fk_blog_posts_author FOREIGN KEY (author_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS blog_comments (
    id INT NOT NULL AUTO_INCREMENT,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_blog_comments_post_id (post_id),
    KEY ix_blog_comments_user_id (user_id),
    CONSTRAINT fk_blog_comments_post FOREIGN KEY (post_id) REFERENCES blog_posts (id) ON DELETE CASCADE,
    CONSTRAINT fk_blog_comments_user FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS blog_likes (
    id INT NOT NULL AUTO_INCREMENT,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_blog_like_post_user (post_id, user_id),
    KEY ix_blog_likes_post_id (post_id),
    KEY ix_blog_likes_user_id (user_id),
    CONSTRAINT fk_blog_likes_post FOREIGN KEY (post_id) REFERENCES blog_posts (id) ON DELETE CASCADE,
    CONSTRAINT fk_blog_likes_user FOREIGN KEY (user_id) REFERENCES users (id)
);