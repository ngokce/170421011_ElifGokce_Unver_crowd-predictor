-- CrowdPredictor Database Setup
-- Bu script'i MySQL'de çalıştırarak database'i oluşturun

-- Database oluştur
CREATE DATABASE IF NOT EXISTS traffic_predictor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE traffic_predictor;

-- Users tablosu
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

-- Search history tablosu
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255),
    datetime TIMESTAMP NOT NULL,
    prediction_result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_datetime (user_id, created_at)
);

-- Favorites tablosu
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255),
    route_name VARCHAR(100),
    prediction_result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Test kullanıcısı ekle (şifre: 123456)
INSERT IGNORE INTO users (name, email, password_hash) VALUES 
('Test Kullanıcı', 'test@example.com', '$2b$12$example_hash_here');

SELECT 'Database kurulumu tamamlandı!' as status; 