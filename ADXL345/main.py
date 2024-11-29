from time import sleep
from machine import Pin, I2C
from ADXL345 import ADXL345

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000) 
adxl345 = ADXL345(i2c, deviceAddress = 0x53)

print(f"DeviceID: {adxl345.GetDeviceID()}")
print(f"Offsets: {adxl345.GetOffsets()}")
print(f"Accelerations: {adxl345.GetAcceleration()}")

adxl345.SetDataFormat(self_test=False, spi=False, int_invert=False, full_res=True, justify=False, range=16)
adxl345.SetPowerControl(Link=False, AutoSleep=False, Measure=True, Sleep=False, WakeUp=8)

print(f"Data format: {bin(adxl345.GetDataFormat())}")
print(f"Interupt source: {bin(adxl345.GetInteruptSource())}")
print(f"DATA_READY interupt source: {adxl345.GetDataReadyInteruptSource()}")

adxl345.SetInteruptEnableConfig(Activity=True)
adxl345.SetThresholdActivity(50)
adxl345.SetActivityInteruptConfig(ActACDC=False, ActZ=True)
adxl345.SetOffsets(0,0,0)

print(f"Activity interupt config: {adxl345.GetActivityInteruptConfig()}")
print(f"Threshold activity: {adxl345.GetThresholdActivity()}")
print(f"Threshold inactivity: {adxl345.GetThresholdInActivity()}")
print(f"Interupt map: {adxl345.GetInteruptMap()}")
print(f"INT_ENABLE: {bin(adxl345.GetInteruptEnableConfig())}")

print(adxl345.GetAcceleration())
adxl345.PerformManualCalibrationConfig()
#print(adxl345.GetAcceleration(IncludeOffset=True))

try:
    while True:
        accele = adxl345.GetAcceleration(IncludeOffset=True)
        print(f"[{accele[0]:.2f}, {accele[1]:.2f}, {accele[2]:.2f}]")
        #print(f"Interupt source: {bin(adxl345.GetInteruptSource())}")
        #print(f"Activity: {adxl345.GetActivityInteruptSource()}")
        sleep(0.1)
except KeyboardInterrupt:
    print("Program terminated by user.")
