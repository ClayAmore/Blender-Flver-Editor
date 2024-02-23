from typing import List
from datetime import *
from .binder import Binder
from .binder_file import BinderFile
from .binder_hash_table import BinderHashTable
from .binder_file_header import BinderFileHeader
from ..util.sf_util import SFUtil
from ..util.binary_reader_ex import BinaryReaderEx

class BND4:
    files: List[BinderFile]
    version: str
    format: Binder.Format
    unk04: bool
    unk05: bool
    big_endian: bool
    bit_big_endian: bool
    unicode: bool
    extended: int

    def __init__(self):
        self.files = []
        self.version = SFUtil.date_to_binder_timestamp(datetime.now())
        self.format = Binder.Format.IDS | Binder.Format.NAMES1 | Binder.Format.NAMES1 | Binder.Format.COMPRESSION
        self.unicode = True
        self.extended = 4

    def Is(self, br: BinaryReaderEx):
        if br.stream.getbuffer().nbytes < 4:
            return False
        
        magic: str = br.get_ascii(0, 4)
        return magic == "BND4"
    
    def read(self, br: BinaryReaderEx):
        file_headers = self.read_header(br)
        for file_header in file_headers:
            self.files.append(file_header.read_file_data(br))

    def read_header(self, br: BinaryReaderEx):
        br.assert_ascii("BND4")

        self.unk04 = br.read_boolean()
        self.unk05 = br.read_boolean()
        br.assert_byte(0)
        br.assert_byte(0)
        
        br.assert_byte(0)
        self.big_endian = br.read_boolean()
        self.bit_big_endian = not br.read_boolean()
        br.assert_byte(0)

        br.set_big_endian(self.big_endian)

        file_count = br.read_int32()
        br.assert_int64(0x40)
        self.version = br.read_fixed_str(8)
        file_header_size: int = br.read_int64()
        br.read_int64()

        self.unicode = br.read_boolean()
        self.format = Binder.read_format(br, self.big_endian, self.bit_big_endian)
        self.extended = br.assert_byte(0, 1, 4, 0x80)
        br.assert_byte(0)

        br.assert_int32(0)

        if self.extended == 4:
            hash_table_offset: int = br.read_int64()
            br.step_in(hash_table_offset)
            BinderHashTable.Assert(br)
            br.step_out()
        else:
            br.assert_int64(0)

        if file_header_size != Binder.get_bnd4_header_size(self.format):
            raise ValueError(f"File header size for format {self.format} is expected to be 0x{Binder.get_bnd4_header_size(self.format):X}, but was 0x{file_header_size:X}")

        file_headers = []
        for i in range(file_count):
            file_headers.append(BinderFileHeader.read_binder4_file_header(br, self.format, self.big_endian, self.bit_big_endian, self.unicode))
        
        return file_headers