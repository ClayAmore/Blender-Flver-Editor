from io import BytesIO
from enum import Enum, IntEnum
from struct import unpack
from typing import Callable, TypeVar, List
from mathutils import Vector, Color
from .binary_reader import BinaryReader, Endian, Whence

class Encoding(Enum):
    ASCII = "ascii"
    SHIFT_JIS = "shift_jis"
    UTF_16 = "utf-16"
    UTF_16_BE = "utf-16-be"

class BinaryReaderEx:
    stream: BytesIO
    binary_reader: BinaryReader
    stack = []
    big_endian = False

    def __init__(self, big_endian: bool, stream: BytesIO):
        self.big_endian = big_endian
        self.stream = stream
        endian = Endian.LITTLE
        if big_endian:
            endian = Endian.BIG
        self.binary_reader = BinaryReader(stream.getvalue(), endian)

    #region HELPER FUNCTIONS
    def set_big_endian(self, big_endian: bool):
        self.big_endian = big_endian
        endian = Endian.LITTLE
        if big_endian:
            endian = Endian.BIG
        self.binary_reader.set_endian(endian)

    def endian(self, f: str | bytes) -> str | bytes:
        return f'>{f}' if self.big_endian else f'<{f}'

    def step_in(self, offset: int):
        self.stack.append(self.stream.tell())
        self.stream.seek(offset)
        self.binary_reader.seek(self.stream.tell())

    def step_out(self):
        self.stream.seek(self.stack.pop())    
        self.binary_reader.seek(self.stream.tell())

    def skip(self, offset: int):
        self.stream.seek(self.stream.tell() + offset)
        self.binary_reader.seek(self.stream.tell())

    def seek(self, pos: int):
        self.stream.seek(pos)
        self.binary_reader.seek(pos)
    #endregion

    #region VALUE
    def get_value(self, read_value: Callable, offset: int):
        self.step_in(offset)
        result = read_value()
        self.step_out()
        return result

    def get_values(self, read_values: Callable, offset:int, length: int):
        self.step_in(offset)
        result = read_values(length)
        self.step_out()
        return result
     
    def assert_value(self, value, type_name, value_format, options):
        for option in options:
            if value == option:
                return value
            
        str_value = str.format(value_format, value)
        str_options = ', '.join(value_format.format(o) for o in options)
        raise AssertionError(f"Read {type_name}: {str_value} | Expected: {str_options} | Ending position: 0x{self.stream.tell():X}")
    #endregion

    #region BYTE
    def assert_byte(self, *options):
        return self.assert_value(ord(self.read_byte()), "Byte", "0x{0:X}", options)

    def read_byte(self):
        self.stream.seek(1, Whence.CUR)
        return self.binary_reader.read_bytes()

    def get_byte(self, offset: int):
        return self.get_value(self.read_byte, offset)

    def get_bytes(self, offset: int, length: int):
        self.step_in(offset)
        result = self.read_bytes(length)
        self.step_out()
        return result
    
    def read_s_byte(self):
        self.stream.seek(1, Whence.CUR)
        signed_byte = unpack('b', self.read_byte())[0]
        return signed_byte
    
    def read_bytes(self, length: int):
        self.stream.seek(length, Whence.CUR)
        bytes = self.binary_reader.read_bytes(length)
        if len(bytes) != length:
             raise ValueError("Remaining size of stream was smaller than requested number of bytes.")
        return bytes

    def read_reversed_bytes(self, length: int):
        bytes = self.read_bytes(length)[::-1]
        return bytes
    #endregion

    #region ASCII
    def assert_ascii(self, *values):
        s = self.read_ascii(len(values[0]))
        valid: bool = False
        for value in values:
            if s == value:
                valid = True
        
        if not valid:
            raise AssertionError(f"Read ASCII: {s} | Expected ASCII: {', '.join(values)} ")

        return s

    def read_chars(self, encoding: Encoding, length: int):
        bytes = self.read_bytes(length)
        return bytes.decode(encoding.value)

    def read_ascii(self, length: int):
        return self.read_chars(Encoding.ASCII, length)

    def get_ascii(self, offset, length):
        self.step_in(offset)
        result = self.read_ascii(length)
        self.step_out()
        return result
    #endregion

    #region INT_16
    def assert_int16(self, *options):
        return self.assert_value(self.read_int16(), "Int16", "0x{0:X}", options)

    def read_int16(self) -> int:
        return unpack(self.endian('h'), self.read_bytes(2))[0]
    
    def read_int16s(self, length: int) -> list:
        result = []
        for i in range(length):
            result.append(self.read_int16())
        return result
    
    def get_int16(self, offset: int):
        return self.get_value(self.read_int16, offset)
    
    def get_int16s(self, offset: int, length: int) -> list:
        return self.get_values(self.read_int16s, offset, length)
    
    #endregion

    #region UINT_16
    def read_uint16(self):
        return unpack(self.endian('H'), self.read_bytes(2))[0]
    
    def read_uint16s(self, length: int):
        result = []
        for i in range(length):
            result.append(self.read_uint16())
        return result

    def get_uint16(self, offset: int):
        return self.get_value(self.read_uint16, offset)
    
    def get_uint16s(self, offset: int, length: int):
        return self.get_values(self.read_uint16s, offset, length)
    #endregion

    #region INT_32
    def assert_int32(self, *options):
        return self.assert_value(self.read_int32(), "Int32", "0x{0:X}", options)

    def read_int32(self) -> int:
        return unpack(self.endian('i'), self.read_bytes(4))[0]
    
    def read_int32s(self, length: int) -> list:
        result = []
        for i in range(length):
            result.append(self.read_int32())
        return result
        
    def get_int32(self, offset: int):
        return self.get_value(self.read_int32, offset)
    
    def get_int32s(self, offset: int, length: int) -> list:
        return self.get_values(self.read_int32s, offset, length)

    #endregion

    #region UINT_32
    def read_uint32(self):
        return unpack(self.endian('I'), self.read_bytes(4))[0]
    #endregion

    #region INT_64
    def assert_int64(self, *options):
        return self.assert_value(self.read_int64(), "Int64", "0x{0:X}", options)

    def read_int64(self) -> int:
        return unpack(self.endian('q'), self.read_bytes(8))[0]

    def get_int64(self, offset: int):
        return self.get_value(self.read_int64, offset)
    #endregion

    #region BOOLEAN
    def read_boolean(self):
        b = ord(self.read_byte())
        if b == 0:
            return False
        elif b == 1:
            return True
        else:
            raise ValueError(f"ReadBoolean encountered non-boolean value: 0x{b:X}")
    #endregion

    #region STRING
    def read_fixed_str(self, length: int):
        bytes = self.read_bytes(length)
        
        for terminator in range(length):
            if bytes[terminator] == 0:
                break
        
        return bytes[0:terminator].decode(Encoding.SHIFT_JIS.value)
    
    def read_chars_terminated(self, encoding: Encoding):
        bytes = bytearray()
        
        b = self.read_byte()
        while(b != 0):
            bytes.append(b)
            b = self.read_byte()
        
        return bytes.decode(encoding.value)

    def read_utf16(self):
        bytes = bytearray()
        pair = self.read_bytes(2)
        while(pair[0] != 0 or pair[1] != 0):
            bytes.append(pair[0])
            bytes.append(pair[1])
            pair = self.read_bytes(2)
        
        if self.big_endian:
            return bytes.decode(Encoding.UTF_16_BE.value)
        else:
            return bytes.decode(Encoding.UTF_16.value)

    def get_utf16(self, offset: int):
        self.step_in(offset)
        result = self.read_utf16()
        self.step_out()
        return result
    
    def read_shift_jis(self):
        return self.read_chars_terminated(Encoding.SHIFT_JIS)


    def get_shit_jis(self, offset: int):
        self.step_in(offset)
        result = self.read_shift_jis()
        self.step_out()
        return result
    #endregion
    
    #region SINGLE
    def read_single(self) -> float:
        return unpack(self.endian('f'), self.read_bytes(4))[0]
    
    def read_singles(self, length: int) -> List[float]:
        result = []
        for i in range(length):
            result[i] = self.read_single()
        return result
        
    def get_single(self, offset: int) ->float:
        return self.get_value(self.read_single(), offset)
    
    def assert_single(self, *options) -> float:
        return self.assert_value(self.read_single(), "Single", "{0}", options)
    #endregion

    #region VECTOR
    def read_vector2(self) -> Vector:
        x: float = self.read_single()
        y: float = self.read_single()
        return Vector((x,y))

    def read_vector3(self) -> Vector:   
        x: float = self.read_single()
        y: float = self.read_single()
        z: float = self.read_single()
        return Vector((x,y,z))

    def read_vector4(self) -> Vector:
        x: float = self.read_single()
        y: float = self.read_single()
        z: float = self.read_single()
        w: float = self.read_single()
        return Vector((x,y,z,w))
    #endregion

    #region COLOR
    def read_arbg(self) -> Vector:
        a: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        r: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        b: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        g: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        return Vector((a, r, b, g))
    
    def read_abgr(self) -> Vector:
        a: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        b: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        g: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        r: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        return Vector((a, r, b, g))
    
    def read_rgba(self) -> Vector:
        r: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        g: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        b: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        a: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        return Vector((a, r, b, g))
    
    def read_bgra(self) -> Vector:
        b: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        g: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        r: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        a: float = int.from_bytes(self.read_byte(), 'big' if self.big_endian else 'little')/255.0
        return Vector((a, r, b, g))
    #endregion

    #region PATTERN
    def assert_pattern(self, length:int, pattern: int):
        bytes = self.read_bytes(length)

        for i, b in enumerate(bytes):
            if b != pattern:
                raise AssertionError(f"Expected {length} 0x{pattern:X2}, got {b:X2} at position {i}")
                
    #endregion
    
    #region ENUM
    T = TypeVar('T')
    def read_enum(self, enum_type: T, read_value: Callable, value_format: str) -> T:
        value = read_value()
        if not value in iter(enum_type):
            str_value = value_format.format(value)
            raise ValueError(f"Read Byte not present in enum: {str_value}")
        return enum_type(value)
    
    def read_enum32(self, enum_type: T) -> T:
        self.read_enum(enum_type, self.read_uint32, "0x{0:X}")
    #endregion