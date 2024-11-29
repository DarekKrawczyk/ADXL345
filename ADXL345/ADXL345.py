from machine import I2C

class ADXL345(object):
    DEVID = const(0x00)
    OFSX = const(0x1E)
    DATAX0 = const(0x32)
    DATA_FORMAT = const(0x31)
    THRESH_ACT = const(0x24)
    THRESH_INACT = const(0x25)
    INT_ENABLE = const(0x2E)
    INT_MAP = const(0x2F)
    POWER_CTL = const(0x2D)
    INT_SOURCE = const(0x30)
    ACT_INACT_CTL = const(0x27)
    
    def __init__(self, i2c: I2C, deviceAddress: int) -> None:
        self.i2c: I2C = i2c
        self.deviceAddress: int = deviceAddress
        self.lastAcceleration: list = [0, 0, 0]
        self.range: dict[int, int] = { 2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11 }
        self.rangeFactor: dict[int, float] = { 2: 0.0039, 4: 0.0078, 8: 0.0156, 16: 0.0312 }
        self.sleepMode: dict[int, int] = { 1: 0b11, 2: 0b10, 4: 0b01, 8: 0b00 }
        self.currentRange: int = 0b11
        self.currentSleepMode: int = 0b00       # 8Hz
        self.dataScaleFactor: float = 0.0039
        self.resultRounding: int = 4

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
    def CurrentRange(self) -> int:
        return self.currentRange

    @property
    def DataScaleFactor(self) -> float:
        return self.dataScaleFactor

    def GetThresholdActivity(self) -> float:
        return self.ReadFromRegister(self.THRESH_ACT) * 0.0625

    def SetThresholdActivity(self, value: int) -> None:
        return self.WriteToRegister(self.THRESH_ACT, value)

    def GetThresholdInActivity(self) -> float:
        return self.ReadFromRegister(self.THRESH_INACT) * 0.0625

    def SetThresholdInActivity(self, value: int) -> None:
        return self.WriteToRegister(self.THRESH_INACT, value)

    def GetDeviceID(self) -> int:
        return self.ReadFromRegister(self.DEVID)

    def GetInteruptEnableConfig(self) -> int:
        return self.ReadFromRegister(self.INT_ENABLE)

    def SetInteruptEnableConfig(self, DataReady: bool = False, SingleTap: bool = False, DoubleTap: bool = False, Activity: bool = False,
                                InActivity: bool = False, FreeFall: bool = False, Watermark: bool = False, Overrun: bool = False) -> None:
        dataFrame: int = (DataReady << 7) | (SingleTap << 6) | (DoubleTap << 5) | (Activity << 4) | (InActivity << 3) | (FreeFall << 2) | (Watermark << 1) | (Overrun)
        self.WriteToRegister(self.INT_ENABLE, dataFrame)

    def GetInteruptMap(self) -> int:
        return self.ReadFromRegister(self.INT_MAP)

    def GetOffsets(self) -> list:
        rawOffsets: bytes = self.ReadFromRegisters(self.OFSX, 3)
        return list(rawOffsets)

    def SetOffsets(self, x: int, y: int, z: int) -> None:
        self.WriteToRegister(self.OFSX, x)
        self.WriteToRegister(self.OFSX + 1, y)
        self.WriteToRegister(self.OFSX + 2, z)

    def GetAcceleration(self) -> list:
        raw: bytes = self.ReadFromRegisters(self.DATAX0, 6)

        x: int = raw[1] << 8 | raw[0]
        y: int = raw[3] << 8 | raw[2]
        z: int = raw[5] << 8 | raw[4]
        
        xx: float = round(self.ParseFromComplementTwo(x) * self.dataScaleFactor, self.resultRounding)
        yy: float = round(self.ParseFromComplementTwo(y) * self.dataScaleFactor, self.resultRounding)
        zz: float = round(self.ParseFromComplementTwo(z) * self.dataScaleFactor, self.resultRounding)
        
        result: list = [xx, yy, zz]
        self.lastAcceleration = result
        return result

    def SetDataFormat(self, self_test: bool, spi: bool, int_invert: bool, full_res: bool, justify: bool, range: int) -> None:
        if range < 2 or range % 2 != 0 or range > 16: return
        rangeFormat: int = self.range.get(range, 0b00)
        dataFrame: int = ((int(self_test) << 7) | (int(spi) << 6) | (int(int_invert) << 5) | (int(full_res) << 3) | (int(justify) << 2)) | rangeFormat
        self.WriteToRegister(self.DATA_FORMAT, dataFrame)

    def GetDataFormat(self) -> int:
        return self.ReadFromRegister(self.DATA_FORMAT)

    def GetInteruptSource(self) -> int:
        return self.ReadFromRegister(self.INT_SOURCE)

    def GetDataReadyInteruptSource(self) -> bool:
        intSrc: int = self.GetInteruptSource() 
        return (intSrc & 0b10000000 == 0b10000000)

    def GetActivityInteruptSource(self) -> bool:
        intSrc: int = self.GetInteruptSource() 
        return (intSrc & 0b00010000 == 0b00010000)

    def GetActivityInteruptConfig(self) -> int:
        return self.ReadFromRegister(self.ACT_INACT_CTL)

    def SetActivityInteruptConfig(self, ActACDC: bool = False, ActX: bool = False, ActY: bool = False, ActZ: bool = False,
                                        InActACDC: bool = False, InActX: bool = False, InActY: bool = False, InActZ: bool = False) -> None:
        dataFrame: int = int(ActACDC << 7) | int(ActX << 6) | int(ActY << 5) | int(ActZ << 4) | int(InActACDC << 3) | int(InActX << 2) | int(InActY << 1) | int(InActZ)
        self.WriteToRegister(self.ACT_INACT_CTL, dataFrame)
    
    def GetPowerControl(self) -> int:
        return self.ReadFromRegister(self.POWER_CTL)
    
    def SetPowerControl(self, Link: bool = False, AutoSleep: bool = False, Measure: bool = False, Sleep: bool = False, WakeUp: int = 0b00) -> None:
        if WakeUp < 1  or WakeUp > 8: return
        sleepMode: int = self.sleepMode.get(WakeUp, 0b00)
        self.currentSleepMode = sleepMode
        dataFrame: int = (int(Link) << 5) | (int(AutoSleep) << 4) | (int(Measure) << 3) | (int(Sleep) << 2) | sleepMode
        self.WriteToRegister(self.POWER_CTL, dataFrame)

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
