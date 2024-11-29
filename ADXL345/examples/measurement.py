from time import sleep
from machine import Pin, I2C
from ADXL345 import ADXL345

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000) 
adxl345 = ADXL345(i2c, deviceAddress = 0x53)

adxl345.SetDataFormat(self_test=False, spi=False, int_invert=False, full_res=True, justify=False, range=16)
adxl345.SetPowerControl(Link=False, AutoSleep=False, Measure=True, Sleep=False, WakeUp=8)

try:
    while True:
        accele = adxl345.GetAcceleration()
        print(f"x,y,z = [{accele[0]:.2f}, {accele[1]:.2f}, {accele[2]:.2f}]")
        sleep(0.1)
except KeyboardInterrupt:
    print("Program terminated")
