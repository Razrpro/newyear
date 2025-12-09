# Примеры использования LED Controller REST API

## Запуск сервера
```bash
python3 led_controller_api.py
```

Swagger UI будет доступен по адресу: **http://localhost:5000/swagger**

---

## REST API Endpoints

### 1. Получить все светодиоды
```bash
curl http://localhost:5000/leds/
```

**Ответ:**
```json
[
  {
    "id": 1,
    "название": "Светодиод 1",
    "pin": 2,
    "состояние": "выкл"
  },
  ...
]
```

---

### 2. Получить один светодиод
```bash
curl http://localhost:5000/leds/5
```

**Ответ:**
```json
{
  "id": 5,
  "название": "Светодиод 5",
  "pin": 6,
  "состояние": "выкл"
}
```

---

### 3. Включить светодиод
```bash
# Способ 1: POST запрос
curl -X POST http://localhost:5000/leds/5/on

# Способ 2: PUT с JSON
curl -X PUT http://localhost:5000/leds/5 \
  -H "Content-Type: application/json" \
  -d '{"состояние": "вкл"}'
```

---

### 4. Выключить светодиод
```bash
# Способ 1: POST запрос
curl -X POST http://localhost:5000/leds/5/off

# Способ 2: PUT с JSON
curl -X PUT http://localhost:5000/leds/5 \
  -H "Content-Type: application/json" \
  -d '{"состояние": "выкл"}'
```

---

### 5. Включить ВСЕ светодиоды
```bash
curl -X PUT http://localhost:5000/leds/ \
  -H "Content-Type: application/json" \
  -d '{"состояние": "вкл"}'
```

---

### 6. Выключить ВСЕ светодиоды
```bash
curl -X PUT http://localhost:5000/leds/ \
  -H "Content-Type: application/json" \
  -d '{"состояние": "выкл"}'
```

---

### 7. Проверка состояния API
```bash
curl http://localhost:5000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "arduino": "connected",
  "port": "/dev/cu.usbserial-210"
}
```

---

## Использование через Swagger UI

1. Откройте браузер: **http://localhost:5000/swagger**
2. Вы увидите интерактивную документацию
3. Раскройте любой endpoint
4. Нажмите "Try it out"
5. Заполните параметры
6. Нажмите "Execute"
7. Увидите результат!

---

## Примеры на Python

### Включить светодиод 3
```python
import requests

response = requests.post('http://localhost:5000/leds/3/on')
print(response.json())
```

### Получить состояние всех светодиодов
```python
import requests

response = requests.get('http://localhost:5000/leds/')
leds = response.json()
for led in leds:
    print(f"LED {led['id']}: {led['состояние']}")
```

### Выключить все светодиоды
```python
import requests

response = requests.put(
    'http://localhost:5000/leds/',
    json={'состояние': 'выкл'}
)
print(response.json())
```

---

## Примеры на JavaScript

### Включить светодиод 7
```javascript
fetch('http://localhost:5000/leds/7/on', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Получить все светодиоды
```javascript
fetch('http://localhost:5000/leds/')
  .then(response => response.json())
  .then(leds => {
    leds.forEach(led => {
      console.log(`LED ${led.id}: ${led.состояние}`);
    });
  });
```

---

## Тестирование последовательности

```bash
# Включаем светодиоды по очереди
for i in {1..12}; do
  curl -X POST http://localhost:5000/leds/$i/on
  sleep 0.5
done

# Выключаем в обратном порядке
for i in {12..1}; do
  curl -X POST http://localhost:5000/leds/$i/off
  sleep 0.5
done
```

---

## Эффект "бегущий огонь"

```bash
#!/bin/bash
# running_light.sh

while true; do
  for i in {1..12}; do
    curl -s -X POST http://localhost:5000/leds/$i/on > /dev/null
    sleep 0.2
    curl -s -X POST http://localhost:5000/leds/$i/off > /dev/null
  done
done
```

Сделайте скрипт исполняемым:
```bash
chmod +x running_light.sh
./running_light.sh
```
