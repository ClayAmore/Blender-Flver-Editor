from enum import IntFlag
from ..util.sf_util import SFUtil
from ..util.binary_reader_ex import BinaryReaderEx

class Binder:
    class FileFlags(IntFlag):
        NONE = 0
        COMPRESSED = 0b0000_0001
        FLAG1 = 0b0000_0010
        FLAG2 = 0b0000_0100
        FLAG3 = 0b0000_1000
        FLAG4 = 0b0001_0000
        FLAG5 = 0b0010_0000
        FLAG6 = 0b0100_0000
        FLAG7 = 0b1000_0000

    class Format(IntFlag):
        NONE = 0
        BIGENDIAN = 0b0000_0001
        IDS = 0b0000_0010
        NAMES1 = 0b0000_0100
        NAMES2 = 0b0000_1000
        LONGOFFSETS = 0b0001_0000
        COMPRESSION = 0b0010_0000
        FLAG6 = 0b0100_0000
        FLAG7 = 0b1000_0000

    @staticmethod
    def read_format(br: BinaryReaderEx, big_endian: bool, bit_big_endian: bool) -> Format:
        raw_format = int.from_bytes(br.read_byte(), 'big' if big_endian else 'little')
        reverse: bool = bit_big_endian or (raw_format & 1) != 0 and (raw_format & 0b1000_0000) == 0
        return Binder.Format(raw_format) if reverse else  Binder.Format(SFUtil.reverse_bits(raw_format))

    @staticmethod
    def read_file_flags(br: BinaryReaderEx, big_endian: bool,  bit_big_endian: bool) -> FileFlags:
        reverse = bit_big_endian
        raw_flags = int.from_bytes(br.read_byte(), 'big' if big_endian else 'little')
        return Binder.FileFlags(raw_flags) if reverse else Binder.FileFlags(SFUtil.reverse_bits(raw_flags))

    @staticmethod
    def get_bnd4_header_size(format: Format) -> int:
        return (0x10 
                + (8 if Binder.has_long_offsets(format) else 4) 
                + (8 if Binder.has_compression(format) else 0) 
                + (4 if Binder.has_ids(format) else 0) 
                + (4 if Binder.has_names(format) else 0) 
                + (8 if format == Binder.Format.NAMES1 else 0))
    
    @staticmethod 
    def has_long_offsets(format: Format) -> bool:
        return (format & Binder.Format.LONGOFFSETS) != 0 
    
    @staticmethod
    def has_compression(format: Format) -> bool:
        return (format & Binder.Format.COMPRESSION) != 0 
    
    @staticmethod
    def has_ids(format: Format) -> bool:
        return (format & Binder.Format.IDS) != 0 
    
    @staticmethod
    def has_names(format: Format) -> bool:
        return (format & (Binder.Format.NAMES1 | Binder.Format.NAMES2)) != 0
    
    @staticmethod 
    def is_compressed(flags: FileFlags):
        return (flags & Binder.FileFlags.COMPRESSED) != 0
    