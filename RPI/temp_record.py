import time
import board
import adafruit_dht

# Initialize DHT22 sensor on GPIO17 (pin 11)
dht_sensor = adafruit_dht.DHT22(board.D17)

while True:
    try:
        temperature = dht_sensor.temperature
        humidity    = dht_sensor.humidity

        if temperature is not None and humidity is not None:
            print(f"Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")
        else:
            print("Sensor error, retrying…")

    except RuntimeError as e:
        print(f"Runtime error: {e}, retrying in 2 seconds…")

    time.sleep(2)
