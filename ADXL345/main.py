from machine import I2C, Pin
from time import sleep

class ADXL345(object):
    DEVID = const(0x00)
    OFSX = const(0x1E)
    DATAX0 = const(0x32)
    
    def __init__(self, i2c: I2C, deviceAddress: int) -> None:
        self.i2c: I2C = i2c
        self.deviceAddress: int = deviceAddress
        self.lastAcceleration: list = [0, 0, 0]
        self.dataScaleFactor: float = 0.00390625

    @property
    def AccX(self) -> float:
        return self.lastAcceleration[0]

    @property
    def AccY(self) -> float:
        return self.lastAcceleration[1]

    @property
    def AccZ(self) -> float:
        return self.lastAcceleration[2]

    @property
    def DeviceID(self) -> int:
        return self.ReadFromRegister(self.DEVID)

    @property
    def OffsetX(self) -> int:
        return self.ReadFromRegister(self.OFSX)

    @OffsetX.setter
    def OffsetX(self, value: int):
        self.WriteToRegister(self.OFSX, value)

    def GetAcceleration(self) -> list:
        raw: bytes = self.ReadFromRegisters(self.DATAX0, 6)

        x: int = raw[1] << 8 | raw[0]
        y: int = raw[3] << 8 | raw[2]
        z: int = raw[5] << 8 | raw[4]
        
        xx: float = round(self.ParseFromComplementTwo(x) * self.dataScaleFactor, 2)
        yy: float = round(self.ParseFromComplementTwo(y) * self.dataScaleFactor, 2)
        zz: float = round(self.ParseFromComplementTwo(z) * self.dataScaleFactor, 2)
        
        result: list = [xx, yy, zz]
        self.lastAcceleration = result
        return result

    def SetDataFormat(self, self_test: bool, spi: bool, int_invert: bool, full_res: bool, justify: bool, range: int) -> None:
        if range % 2 != 0: return
        print(range)
        dataFrame: int = ((int(self_test) << 7) | (int(spi) << 6) | (int(int_invert) << 5) | (int(full_res) << 3) | (int(justify) << 2)) | 4# & range
        print(bin(dataFrame))    

    def GetPowerControl(self) -> int:
        return 1
    
    def SetPowerControl(self, config: int) -> None:
        return None

    def WriteToRegister(self, register: int, value: int) -> None:
        self.i2c.writeto_mem(self.deviceAddress, register, bytearray([value]))
    
    def ReadFromRegisters(self, firstRegister: int, count: int) -> bytes:
        return self.i2c.readfrom_mem(self.deviceAddress, firstRegister, count)
    
    def ReadFromRegister(self, register: int) -> int:
        return self.ReadFromRegisters(register, 1)[0]

    def ParseFromComplementTwo(self, value: int, bits: int = 16) -> int:
        if value & (1 << (bits - 1)):
            value -= (1 << bits)
        return value

# Initialize I2C and configure ADXL345
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)  # Configure I2C

# Configure ADXL345 (0x53 is the default I2C address)
address = 0x53

adxl345 = ADXL345(i2c, address)

print(adxl345.DeviceID)
print(adxl345.OffsetX)
adxl345.OffsetX = 0
print(adxl345.OffsetX)
print(adxl345.GetAcceleration())
adxl345.SetDataFormat(True, False, True, True, False, 16)

device_id = i2c.readfrom_mem(address, 0x00, 1)[0]
if device_id != 0xE5:
    print(f"Error: Unexpected device ID {device_id}")
else:
    print(f"ADXL345 detected with ID: {hex(device_id)}")

# Configure power control and data format
i2c.writeto_mem(address, 0x2D, b'\x08')
i2c.writeto_mem(address, 0x31, b'\x0B') 

try:
    while True:
        #ReadAccele(i2c)
        sleep(0.1)
except KeyboardInterrupt:
    print("Program terminated by user.")
