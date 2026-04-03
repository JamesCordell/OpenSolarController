import time
from w1thermsensor import W1ThermSensor, Sensor

sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id="00000036061c")
temp_c = sensor.get_temperature()
while True:
    temp_c = sensor.get_temperature()
    print(temp_c)
    time.sleep(1)
