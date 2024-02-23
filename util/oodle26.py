from ctypes import *
from enum import Enum
from os import getcwd

oodle26DLL = cdll.LoadLibrary(getcwd() + "\\lib\\oo2core_6_win64.dll")

class oodlelz_fuzzsafe(Enum):
    OODLELZ_FUZZSAFE_NO = 0 
    OODLELZ_FUZZSAFE_YES = 1

class oodlelz_checkcrc(Enum):
    OODLELZ_CHECKCRC_NO = 0
    OODLELZ_CHECKCRC_YES = 1
    OODLELZ_CHECKCRC_FORCE32 = 0x40000000

class oodlelz_verbosity(Enum):
    OODLELZ_VERBOSITY_NONE = 0
    OODLELZ_VERBOSITY_MINIMAL = 1
    OODLELZ_VERBOSITY_SOME = 2
    OODLELZ_VERBOSITY_LOTS = 3
    OODLELZ_VERBOSITY_FORCE32 = 0x40000000

class oodlelz_decode_threadphase(Enum):
    OODLELZ_DECODE_THREADPHASE1 = 1
    OODLELZ_DECODE_THREADPHASE2 = 2
    OODLELZ_DECODE_THREADPHASEALL = 3
    OODLELZ_DECODE_UNTHREADED = OODLELZ_DECODE_THREADPHASEALL


class Oodle26:
    @staticmethod
    def decompress(source: bytes, uncompressed_size: int) -> bytearray:
        decoded_buffer_size = oodle26DLL.OodleLZ_GetDecodeBufferSize(uncompressed_size, True)
        raw_buf = bytearray(decoded_buffer_size)
        char_array = c_char * decoded_buffer_size
        raw_len: int = oodle26DLL.OodleLZ_Decompress(
            cast(source, c_void_p), 
            len(source), 
            char_array.from_buffer(raw_buf), 
            uncompressed_size,
            c_int(oodlelz_fuzzsafe.OODLELZ_FUZZSAFE_YES.value),
            c_int(oodlelz_checkcrc.OODLELZ_CHECKCRC_NO.value),
            c_int(oodlelz_verbosity.OODLELZ_VERBOSITY_NONE.value),
            c_void_p(None),
            c_int(0),
            c_void_p(None),
            c_void_p(None),
            c_void_p(None),
            c_int(0),
            c_int(oodlelz_decode_threadphase.OODLELZ_DECODE_UNTHREADED.value)
        )
        raw_buf.zfill(raw_len - decoded_buffer_size)
        return raw_buf