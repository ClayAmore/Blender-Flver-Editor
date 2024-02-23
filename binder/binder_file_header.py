from .binder import Binder
from .binder_file import BinderFile
from ..util.binary_reader_ex import BinaryReaderEx
from ..formats.dcx import DCX

class BinderFileHeader:
    file_flags: Binder.FileFlags
    id: int
    name: str
    compression_type: DCX.CompressionType
    compressed_size: int
    uncompressed_size: int
    data_offset: int

    def __init__(self, *args):
        self.file_flags = Binder.FileFlags.FLAG1
        self.id = -1
        self.name = None
        self.compression_type = DCX.CompressionType.ZLIB
        self.compressed_size = -1
        self.uncompressed_size = -1
        self.data_offset = -1
        
        if args:
            if isinstance(args[0], Binder.FileFlags):
                self.flags = args[0]

            if len(args) > 1 and isinstance(args[1], int):
                self.id = args[1]

            if len(args) > 2 and isinstance(args[2], str):
                self.name = args[2]

            if len(args) > 3 and isinstance(args[3], int):
                self.compressed_size = args[3]

            if len(args) > 4 and isinstance(args[4], int):
                self.uncompressed_size = args[4]

            if len(args) > 5 and isinstance(args[5], int):
                self.data_offset = args[5]


    def read_file_data(self, br: BinaryReaderEx):
        bytes = bytearray()
        compression_type = DCX.CompressionType.ZLIB
        if Binder.is_compressed(self.file_flags):
            bytes = br.get_bytes(self.data_offset, self.compressed_size)
            bytes = DCX.decompress(bytes, compression_type)
        else:
            bytes = br.get_bytes(self.data_offset, self.compressed_size)
        
        binder_file = BinderFile(self.flags, self.id, self.name, bytes)
        binder_file.compression_type = compression_type

        return binder_file


    @staticmethod
    def read_binder4_file_header(br: BinaryReaderEx, format: Binder.Format, big_endian: bool, bit_big_endian: bool, unicode: bool):
        flags = Binder.read_file_flags(br, big_endian, bit_big_endian)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_int32(-1)
        
        compressed_size = br.read_int64()

        uncompressed_size: int = -1
        if Binder.has_compression(format):
            uncompressed_size = br.read_int64()

        data_offset: int
        if Binder.has_long_offsets(format):
            data_offset = br.read_int64()
        else:
            data_offset = br.read_int32()
        
        id: int = -1
        if Binder.has_ids(format):
            id = br.read_int32()
        
        name: str = None
        if Binder.has_names(format):
            name_offset = br.read_uint32()
            if unicode:
                name = br.get_utf16(name_offset)
            else:
                name = br.get_shit_jis(name_offset)
        
        if format == Binder.Format.NAMES1:
            id = br.read_int32()
            br.assert_int32(0)

        return BinderFileHeader(flags, id, name, compressed_size, uncompressed_size, data_offset)

    

