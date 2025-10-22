#https://docs.circuitpython.org/projects/ds3231/en/latest/
import adafruit_ds3231
import time
import board

i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)

rtc.datetime = time.struct_time((2017,1,9,15,6,0,0,9,-1))

t = rtc.datetime
print(t)
print(t.tm_hour, t.tm_min)