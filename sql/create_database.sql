-- Create database
CREATE DATABASE IF NOT EXISTS voucher_db;
USE voucher_db;

-- Create vouchers table
CREATE TABLE IF NOT EXISTS vouchers (
    code VARCHAR(50) PRIMARY KEY NOT NULL UNIQUE,
    discount_percentage FLOAT NOT NULL CHECK (discount_percentage > 0 AND discount_percentage <= 100),
    expiration_date DATETIME NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_active (active),
    INDEX idx_expiration_date (expiration_date),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;