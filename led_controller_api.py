#!/usr/bin/env python3
"""
LED Controller REST API - управляет светодиодами Arduino через REST API
Включает Swagger UI для тестирования
"""

import serial
import time
import logging
from threading import Thread, Lock
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация Arduino
ARDUINO_PORT = '/dev/cu.usbserial-210'  # Измените на ваш порт
BAUDRATE = 9600

# Flask приложение
app = Flask(__name__)
CORS(app)

# Swagger/OpenAPI документация
api = Api(
    app,
    version='1.0',
    title='LED Controller API',
    description='REST API для управления 12 светодиодами на Arduino UNO',
    doc='/swagger'  # Swagger UI доступен по адресу /swagger
)

# Namespace для API
ns = api.namespace('leds', description='Операции со светодиодами')

# Модели для Swagger
led_model = api.model('LED', {
    'id': fields.Integer(required=True, description='ID светодиода (1-12)'),
    'название': fields.String(required=True, description='Название светодиода'),
    'pin': fields.Integer(required=True, description='Номер пина Arduino (2-13)'),
    'состояние': fields.String(required=True, description='Состояние: вкл или выкл')
})

led_update_model = api.model('LEDUpdate', {
    'состояние': fields.String(required=True, description='Новое состояние: вкл или выкл', enum=['вкл', 'выкл'])
})

led_bulk_update_model = api.model('LEDBulkUpdate', {
    'состояние': fields.String(required=True, description='Состояние для всех светодиодов: вкл или выкл', enum=['вкл', 'выкл'])
})


class LEDController:
    """Контроллер для управления светодиодами"""
    
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.lock = Lock()
        
        # Состояния светодиодов в памяти (pin -> состояние)
        self.leds = {
            1: {'id': 1, 'название': 'Светодиод 1', 'pin': 2, 'состояние': 'выкл'},
            2: {'id': 2, 'название': 'Светодиод 2', 'pin': 3, 'состояние': 'выкл'},
            3: {'id': 3, 'название': 'Светодиод 3', 'pin': 4, 'состояние': 'выкл'},
            4: {'id': 4, 'название': 'Светодиод 4', 'pin': 5, 'состояние': 'выкл'},
            5: {'id': 5, 'название': 'Светодиод 5', 'pin': 6, 'состояние': 'выкл'},
            6: {'id': 6, 'название': 'Светодиод 6', 'pin': 7, 'состояние': 'выкл'},
            7: {'id': 7, 'название': 'Светодиод 7', 'pin': 8, 'состояние': 'выкл'},
            8: {'id': 8, 'название': 'Светодиод 8', 'pin': 9, 'состояние': 'выкл'},
            9: {'id': 9, 'название': 'Светодиод 9', 'pin': 10, 'состояние': 'выкл'},
            10: {'id': 10, 'название': 'Светодиод 10', 'pin': 11, 'состояние': 'выкл'},
            11: {'id': 11, 'название': 'Светодиод 11', 'pin': 12, 'состояние': 'выкл'},
            12: {'id': 12, 'название': 'Светодиод 12', 'pin': 13, 'состояние': 'выкл'},
        }
        
        self.connect_arduino()
    
    def connect_arduino(self):
        """Подключение к Arduino"""
        try:
            self.serial_connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Ждем инициализации Arduino
            logger.info(f"Подключено к Arduino на порту {self.port}")
            
            # Читаем приветственное сообщение
            if self.serial_connection.in_waiting:
                response = self.serial_connection.readline().decode('utf-8').strip()
                logger.info(f"Arduino: {response}")
            
            return True
        except serial.SerialException as e:
            logger.error(f"Ошибка подключения к Arduino: {e}")
            logger.warning("Работа в режиме эмуляции (без Arduino)")
            self.serial_connection = None
            return False
    
    def send_command(self, pin, state):
        """
        Отправка команды Arduino
        
        :param pin: Номер пина
        :param state: Состояние ('вкл' или 'выкл')
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.warning(f"Arduino не подключен. Команда эмулирована: pin={pin}, state={state}")
            return True
        
        with self.lock:
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
    
    def get_all_leds(self):
        """Получить состояние всех светодиодов"""
        return list(self.leds.values())
    
    def get_led(self, led_id):
        """Получить состояние одного светодиода"""
        return self.leds.get(led_id)
    
    def update_led(self, led_id, state):
        """Обновить состояние светодиода"""
        if led_id not in self.leds:
            return None
        
        led = self.leds[led_id]
        pin = led['pin']
        
        # Отправляем команду на Arduino
        if self.send_command(pin, state):
            led['состояние'] = state
            logger.info(f"Обновлен LED {led_id} (pin {pin}): {state}")
            return led
        else:
            return None
    
    def update_all_leds(self, state):
        """Обновить состояние всех светодиодов"""
        for led_id in self.leds:
            self.update_led(led_id, state)
        return self.get_all_leds()
    
    def cleanup(self):
        """Закрытие соединения"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Последовательный порт закрыт")


# Глобальный экземпляр контроллера
controller = LEDController(ARDUINO_PORT, BAUDRATE)


# REST API endpoints

@ns.route('/')
class LEDList(Resource):
    """Операции со всеми светодиодами"""
    
    @ns.doc('list_leds')
    @ns.marshal_list_with(led_model)
    def get(self):
        """Получить список всех светодиодов"""
        return controller.get_all_leds()
    
    @ns.doc('update_all_leds')
    @ns.expect(led_bulk_update_model)
    @ns.marshal_list_with(led_model)
    def put(self):
        """Обновить состояние всех светодиодов"""
        state = api.payload.get('состояние')
        
        if state not in ['вкл', 'выкл']:
            api.abort(400, "Состояние должно быть 'вкл' или 'выкл'")
        
        return controller.update_all_leds(state)


@ns.route('/<int:led_id>')
@ns.param('led_id', 'Идентификатор светодиода (1-12)')
class LED(Resource):
    """Операции с отдельным светодиодом"""
    
    @ns.doc('get_led')
    @ns.marshal_with(led_model)
    def get(self, led_id):
        """Получить состояние светодиода"""
        led = controller.get_led(led_id)
        if led is None:
            api.abort(404, f"Светодиод {led_id} не найден")
        return led
    
    @ns.doc('update_led')
    @ns.expect(led_update_model)
    @ns.marshal_with(led_model)
    def put(self, led_id):
        """Обновить состояние светодиода"""
        state = api.payload.get('состояние')
        
        if state not in ['вкл', 'выкл']:
            api.abort(400, "Состояние должно быть 'вкл' или 'выкл'")
        
        led = controller.update_led(led_id, state)
        if led is None:
            api.abort(404, f"Светодиод {led_id} не найден или ошибка обновления")
        
        return led


@ns.route('/<int:led_id>/on')
@ns.param('led_id', 'Идентификатор светодиода (1-12)')
class LEDOn(Resource):
    """Включить светодиод"""
    
    @ns.doc('turn_on_led')
    @ns.marshal_with(led_model)
    def post(self, led_id):
        """Включить светодиод"""
        led = controller.update_led(led_id, 'вкл')
        if led is None:
            api.abort(404, f"Светодиод {led_id} не найден")
        return led


@ns.route('/<int:led_id>/off')
@ns.param('led_id', 'Идентификатор светодиода (1-12)')
class LEDOff(Resource):
    """Выключить светодиод"""
    
    @ns.doc('turn_off_led')
    @ns.marshal_with(led_model)
    def post(self, led_id):
        """Выключить светодиод"""
        led = controller.update_led(led_id, 'выкл')
        if led is None:
            api.abort(404, f"Светодиод {led_id} не найден")
        return led


@app.route('/health')
def health():
    """Проверка состояния API"""
    arduino_status = "connected" if controller.serial_connection and controller.serial_connection.is_open else "disconnected"
    return jsonify({
        'status': 'ok',
        'arduino': arduino_status,
        'port': ARDUINO_PORT
    })


if __name__ == '__main__':
    try:
        logger.info("=" * 70)
        logger.info("LED Controller REST API запущен")
        logger.info("=" * 70)
        logger.info("Swagger UI: http://localhost:5001/swagger")
        logger.info("API Docs: http://localhost:5001/")
        logger.info("Health Check: http://localhost:5001/health")
        logger.info("=" * 70)
        
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        logger.info("\nОстановка сервера...")
    finally:
        controller.cleanup()
