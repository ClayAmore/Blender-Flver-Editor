from io import BytesIO
from typing import List
from datetime import *
from ..formats.dcx import DCX
from .binary_reader_ex import BinaryReaderEx

class SFUtil:
    @staticmethod
    def get_decompressed_br(br: BinaryReaderEx, compression: DCX.CompressionType) -> BinaryReaderEx:
        if DCX.is_dcx(br): 
            bytes: bytearray = DCX.decompress(br, compression)
            return BinaryReaderEx(False, BytesIO(bytes))
        else:
            return br

    @staticmethod
    def date_to_binder_timestamp(date_time: datetime):
        year: int = date_time.year - 2000
        if year < 0 or year > 99:
            raise ValueError("BND timestamp year must be between 2000 and 2099 inclusive.")

        month: chr = chr(date_time.month + ord('A'))
        day: int = date_time.day
        hour: chr = chr(date_time.hour + ord('A'))
        minute: int = date_time.minute

        return f"{year:02d}{month}{day}{hour}{minute}".ljust(8, '\0')
    
    @staticmethod
    def reverse_bits(value):
        return (((value & 0b00000001) << 7) |
                ((value & 0b00000010) << 5) |
                ((value & 0b00000100) << 3) |
                ((value & 0b00001000) << 1) |
                ((value & 0b00010000) >> 1) |
                ((value & 0b00100000) >> 3) |
                ((value & 0b01000000) >> 5) |
                ((value & 0b10000000) >> 7))
    
    @staticmethod
    def dictionize(items: List):
        dictionary = {}
        for i, item in enumerate(items):
            dictionary[i] = item
        return dictionary
