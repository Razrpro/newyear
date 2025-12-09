/*
 * Arduino UNO LED Controller
 * Управляет 12 светодиодами по командам от Python приложения
 *
 * Команды:
 * - "ON:X" - включить светодиод на пине X
 * - "OFF:X" - выключить светодиод на пине X
 *
 * Подключение: пины D2-D13 (12 светодиодов)
 * Arduino UNO имеет те же цифровые пины 2-13, что и Nano
 */

// Массив пинов для 12 светодиодов
const int LED_PINS[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
const int NUM_LEDS = 12;

void setup()
{
    // Инициализация последовательного порта
    Serial.begin(9600);

    // Настройка всех пинов как выходы и выключение всех светодиодов
    for (int i = 0; i < NUM_LEDS; i++)
    {
        pinMode(LED_PINS[i], OUTPUT);
        digitalWrite(LED_PINS[i], LOW);
    }

    Serial.println("Arduino LED Controller Ready");
}

void loop()
{
    // Проверяем наличие данных в последовательном порту
    if (Serial.available() > 0)
    {
        String command = Serial.readStringUntil('\n');
        command.trim(); // Удаляем пробелы и символы переноса строки

        processCommand(command);
    }
}

void processCommand(String command)
{
    // Разбираем команду формата "ON:X" или "OFF:X"
    int separatorIndex = command.indexOf(':');

    if (separatorIndex == -1)
    {
        Serial.println("ERROR: Invalid command format");
        return;
    }

    String action = command.substring(0, separatorIndex);
    int pin = command.substring(separatorIndex + 1).toInt();

    // Проверяем, что пин существует в нашем массиве
    bool validPin = false;
    for (int i = 0; i < NUM_LEDS; i++)
    {
        if (LED_PINS[i] == pin)
        {
            validPin = true;
            break;
        }
    }

    if (!validPin)
    {
        Serial.print("ERROR: Invalid pin ");
        Serial.println(pin);
        return;
    }

    // Выполняем команду
    if (action == "ON")
    {
        digitalWrite(pin, HIGH);
        Serial.print("OK: LED on pin ");
        Serial.print(pin);
        Serial.println(" turned ON");
    }
    else if (action == "OFF")
    {
        digitalWrite(pin, LOW);
        Serial.print("OK: LED on pin ");
        Serial.print(pin);
        Serial.println(" turned OFF");
    }
    else
    {
        Serial.print("ERROR: Unknown action ");
        Serial.println(action);
    }
}
