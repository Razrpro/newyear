-- SQL скрипт для создания базы данных и таблицы для управления светодиодами

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS led_control;
USE led_control;

-- Создание таблицы для светодиодов
CREATE TABLE IF NOT EXISTS leds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    название VARCHAR(100) NOT NULL COMMENT 'Название светодиода',
    pin INT NOT NULL COMMENT 'Номер пина Arduino (2-13)',
    состояние VARCHAR(10) NOT NULL DEFAULT 'выкл' COMMENT 'Состояние: вкл или выкл',
    UNIQUE KEY unique_pin (pin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Вставка данных для 12 светодиодов (пины 2-13 на Arduino Nano)
INSERT INTO leds (название, pin, состояние) VALUES
    ('Светодиод 1', 2, 'выкл'),
    ('Светодиод 2', 3, 'выкл'),
    ('Светодиод 3', 4, 'выкл'),
    ('Светодиод 4', 5, 'выкл'),
    ('Светодиод 5', 6, 'выкл'),
    ('Светодиод 6', 7, 'выкл'),
    ('Светодиод 7', 8, 'выкл'),
    ('Светодиод 8', 9, 'выкл'),
    ('Светодиод 9', 10, 'выкл'),
    ('Светодиод 10', 11, 'выкл'),
    ('Светодиод 11', 12, 'выкл'),
    ('Светодиод 12', 13, 'выкл');

-- Просмотр данных
SELECT * FROM leds;
