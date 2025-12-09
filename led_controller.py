#!/usr/bin/env python3
"""
LED Controller - управляет светодиодами Arduino через MySQL базу данных
Опрашивает БД каждую секунду и обновляет состояние светодиодов
"""

import serial
import mysql.connector
from mysql.connector import Error
import time
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LEDController:
    def __init__(self, arduino_port, baudrate, db_config):
        """
        Инициализация контроллера LED
        
        :param arduino_port: Порт Arduino (например, '/dev/ttyUSB0' или 'COM3')
        :param baudrate: Скорость обмена данными (по умолчанию 9600)
        :param db_config: Словарь с параметрами подключения к БД
        """
        self.arduino_port = arduino_port
        self.baudrate = baudrate
        self.db_config = db_config
        self.serial_connection = None
        self.db_connection = None
        self.led_states = {}  # Кэш состояний светодиодов
        
    def connect_arduino(self):
        """Подключение к Arduino"""
        try:
            self.serial_connection = serial.Serial(
                self.arduino_port, 
                self.baudrate, 
                timeout=1
            )
            time.sleep(2)  # Ждем инициализации Arduino
            logger.info(f"Подключено к Arduino на порту {self.arduino_port}")
            
            # Читаем приветственное сообщение от Arduino
            if self.serial_connection.in_waiting:
                response = self.serial_connection.readline().decode('utf-8').strip()
                logger.info(f"Arduino: {response}")
            
            return True
        except serial.SerialException as e:
            logger.error(f"Ошибка подключения к Arduino: {e}")
            return False
    
    def connect_database(self):
        """Подключение к MySQL базе данных"""
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            if self.db_connection.is_connected():
                logger.info("Подключено к MySQL базе данных")
                return True
        except Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False
        return False
    
    def send_command(self, pin, state):
        """
        Отправка команды Arduino
        
        :param pin: Номер пина
        :param state: Состояние ('вкл' или 'выкл')
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Последовательный порт не открыт")
            return False
        
        # Формируем команду
        action = "ON" if state.lower() in ['вкл', 'on', '1'] else "OFF"
        command = f"{action}:{pin}\n"
        
        try:
            # Отправляем команду
            self.serial_connection.write(command.encode('utf-8'))
            self.serial_connection.flush()
            
            # Читаем ответ
            time.sleep(0.1)
            if self.serial_connection.in_waiting:
                response = self.serial_connection.readline().decode('utf-8').strip()
                logger.info(f"Arduino ответ: {response}")
                
                if response.startswith("OK"):
                    return True
                elif response.startswith("ERROR"):
                    logger.error(f"Arduino ошибка: {response}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки команды: {e}")
            return False
    
    def get_leds_from_db(self):
        """
        Получение состояния всех светодиодов из БД
        
        :return: Список кортежей (id, название, pin, состояние)
        """
        if not self.db_connection or not self.db_connection.is_connected():
            logger.error("Нет подключения к БД")
            return []
        
        try:
            cursor = self.db_connection.cursor()
            query = "SELECT id, название, pin, состояние FROM leds"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Ошибка запроса к БД: {e}")
            # Пытаемся переподключиться
            self.connect_database()
            return []
    
    def update_leds(self):
        """
        Обновление состояния светодиодов на основе данных из БД
        """
        leds = self.get_leds_from_db()
        
        for led in leds:
            led_id, название, pin, состояние = led
            
            # Проверяем, изменилось ли состояние
            cache_key = f"{pin}"
            if cache_key in self.led_states and self.led_states[cache_key] == состояние:
                continue  # Состояние не изменилось, пропускаем
            
            # Отправляем команду на Arduino
            logger.info(f"Обновление LED '{название}' (pin {pin}): {состояние}")
            if self.send_command(pin, состояние):
                # Обновляем кэш только при успешной отправке
                self.led_states[cache_key] = состояние
    
    def run(self):
        """
        Основной цикл работы приложения
        """
        logger.info("Запуск LED Controller...")
        
        # Подключаемся к Arduino
        if not self.connect_arduino():
            logger.error("Не удалось подключиться к Arduino. Завершение.")
            return
        
        # Подключаемся к БД
        if not self.connect_database():
            logger.error("Не удалось подключиться к БД. Завершение.")
            return
        
        logger.info("Начало мониторинга БД (опрос каждую секунду)...")
        logger.info("Нажмите Ctrl+C для остановки")
        
        try:
            while True:
                self.update_leds()
                time.sleep(1)  # Опрос каждую секунду
        except KeyboardInterrupt:
            logger.info("\nОстановка по запросу пользователя...")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Закрытие соединений"""
        logger.info("Закрытие соединений...")
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Последовательный порт закрыт")
        
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            logger.info("Соединение с БД закрыто")


def main():
    """Точка входа в приложение"""
    
    # Конфигурация Arduino
    ARDUINO_PORT = '/dev/cu.usbserial-210'  # Для macOS: /dev/cu.usbmodem* или /dev/cu.usbserial-*
                                             # Для Linux: /dev/ttyACM0 или /dev/ttyUSB0
                                             # Для Windows: COM3, COM4, и т.д.
    BAUDRATE = 9600
    
    # Конфигурация базы данных
    DB_CONFIG = {
        'host': 'localhost',       # Адрес сервера MySQL
        'database': 'led_control', # Имя базы данных
        'user': 'root',           # Имя пользователя
        'password': 'password'     # Пароль
    }
    
    # Создаем и запускаем контроллер
    controller = LEDController(ARDUINO_PORT, BAUDRATE, DB_CONFIG)
    controller.run()


if __name__ == "__main__":
    main()
