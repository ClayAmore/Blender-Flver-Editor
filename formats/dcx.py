import zlib
from enum import Enum
from io import BytesIO
from ..util.binary_reader_ex import BinaryReaderEx
from ..util.oodle26 import Oodle26

class DCX:
    class CompressionType(Enum): 
        UNKOWN = 0
        NONE = 1
        ZLIB = 2
        DCP_EDGE = 3 
        DCP_DFLT = 4
        DCX_EDGE = 5
        DCX_DFLT_10000_24_9 = 6 
        DCX_DFLT_10000_44_9 = 7 
        DCX_DFLT_11000_44_8 = 8
        DCX_DFLT_11000_44_9 = 9 
        DCX_DFLT_11000_44_9_15 = 10
        DCX_KRAK = 11

    @staticmethod
    def is_dcx(br: BinaryReaderEx):
        if br.stream.getbuffer().nbytes < 4: 
            return False
        magic = br.get_ascii(0, 4)
        return magic == "DCP\0" or magic == "DCX\0"

    @staticmethod
    def decompress(br: BinaryReaderEx, compression: CompressionType) -> bytearray:
        br.set_big_endian(True)
        compression = DCX.CompressionType.UNKOWN

        magic = br.read_ascii(4)
        if magic == "DCP\0":
            file_format = br.get_ascii(4,4)
            if file_format == "DFLT":
                compression = DCX.CompressionType.DCP_DFLT
            elif file_format == "EDGE":
                compression = DCX.CompressionType.DCP_EDGE
        elif magic == "DCX\0":
            file_format = br.get_ascii(0x28, 4)
            if file_format == "EDGE":
                compression = DCX.CompressionType.DCX_EDGE
            elif file_format == "DFLT":
                unk04 = br.get_int32(0x4)
                unk10 = br.get_int32(0x10)
                unk30 = int.from_bytes(br.get_byte(0x30), 'big')
                unk38 = int.from_bytes(br.get_byte(0x38), 'big')

                if unk04 == 0x10000 and unk10 == 0x24 and unk30 == 9 and unk38 == 0:
                    compression =  DCX.CompressionType.DCX_DFLT_10000_24_9
                elif unk04 == 0x10000 and unk10 == 0x44 and unk30 == 9 and unk38 == 0:
                    compression =  DCX.CompressionType.DCX_DFLT_10000_44_9
                elif unk04 == 0x11000 and unk10 == 0x44 and unk30 == 8 and unk38 == 0:
                    compression =  DCX.CompressionType.DCX_DFLT_11000_44_8
                elif unk04 == 0x11000 and unk10 == 0x44 and unk30 == 9 and unk38 == 0:
                    compression =  DCX.CompressionType.DCX_DFLT_11000_44_9
                elif unk04 == 0x11000 and unk10 == 0x44 and unk30 == 9 and unk38 == 15:
                    compression =  DCX.CompressionType.DCX_DFLT_11000_44_9_15
            elif file_format == "KRAK":
                compression = DCX.CompressionType.DCX_KRAK
        else:
            b0 = int.from_bytes(br.get_byte(0), 'big')
            b1 = int.from_bytes(br.get_byte(1), 'big')
            if b0 == 0x78 and (b1 == 0x01 or b1 == 0x5E or b1 == 0x9C or b1 == 0xDA):
                compression = DCX.CompressionType.ZLIB

        br.seek(0)

        if compression == DCX.CompressionType.ZLIB:
            return DCX.read_zlib(br, len(br.stream))
        elif compression == DCX.CompressionType.DCP_EDGE:
            return DCX.decompress_dcp_edge(br)
        elif compression == DCX.CompressionType.DCP_DFLT:
            return DCX.decompress_dcp_dflt(br)
        elif compression == DCX.CompressionType.DCP_EDGE:
            return DCX.decompress_dcx_edge(br)
        elif (compression == DCX.CompressionType.DCX_DFLT_10000_24_9 or
            compression == DCX.CompressionType.DCX_DFLT_10000_44_9 or
            compression == DCX.CompressionType.DCX_DFLT_11000_44_8 or
            compression == DCX.CompressionType.DCX_DFLT_11000_44_9 or
            compression == DCX.CompressionType.DCX_DFLT_11000_44_9_15):
            return DCX.decompress_dcx_dflt(br, compression)
        elif compression == DCX.CompressionType.DCX_KRAK:
            return DCX.decompress_dcx_krak(br)
        else:
            raise TypeError("Unknown DCX format.")

    @staticmethod 
    def read_zlib(br: BinaryReaderEx, compressed_size: int) -> bytearray:
        br.assert_byte(0x78)
        br.assert_byte(0x01, 0x5E, 0x9C, 0xDA)
        compressed = br.read_bytes(compressed_size-2)
        decompressed = zlib.decompress(compressed, wbits = -zlib.MAX_WBITS)
        return bytearray(decompressed)

    @staticmethod
    def decompress_dcp_edge(br: BinaryReaderEx) -> bytearray:
        br.assert_ascii("DCP\0")
        br.assert_ascii("EDGE")
        br.assert_int32(0x20)
        br.assert_int32(0x9000000)
        br.assert_int32(0x10000)
        br.assert_int32(0x0)
        br.assert_int32(0x0)
        br.assert_int32(0x00100100)

        br.assert_ascii("DCS\0")
        uncompressed_size = br.read_int32()
        compressed_size = br.read_int32()

        br.assert_int32(0)
        data_start = br.position
        br.skip(compressed_size)

        br.assert_ascii("DCA\0")
        dca_size = br.read_int32()

        br.assert_ascii("EgdT")
        br.assert_int32(0x00010000)
        br.assert_int32(0x20)
        br.assert_int32(0x10)
        br.assert_int32(0x10000)
        egdt_size = br.read_int32()
        chunk_count = br.read_int32()
        br.assert_int32(0x100000)

        if egdt_size != 0x20 + chunk_count * 0x10:
            raise ValueError("Unexpected EgdT size in EDGE DCX.")
        
        decompressed = bytearray(uncompressed_size)
        dcmp_stream = BytesIO(decompressed)
        for i in range(chunk_count):
            br.assert_int32(0)
            offset = br.read_int32()
            size = br.read_int32()
            compressed = br.assert_int32(0, 1) == 1

            chunk = br.get_bytes(data_start + offset, size)

            if compressed:
                cmp_stream = BytesIO(chunk)
                decompressed_chunk = zlib.decompress(cmp_stream.read())
                dcmp_stream.write(decompressed_chunk)
            else:
                dcmp_stream.write(chunk)
        
        return dcmp_stream.getvalue()
    
    @staticmethod
    def decompress_dcp_dflt(br: BinaryReaderEx) -> bytearray:
        br.assert_ascii("DCP\0")
        br.assert_ascii("DFLT")
        br.assert_int32(0x20)
        br.assert_int32(0x9000000)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0x00010100)

        br.assert_ascii("DCS\0")
        uncompressed_size = br.read_int32()
        compressed_size = br.read_int32()

        decompressed = bytearray(uncompressed_size)

        br.assert_ascii("DCA\0")
        br.assert_int32(8)

        return decompressed
    

    @staticmethod
    def decompress_dcx_edge(br: BinaryReaderEx) -> bytearray:
        br.assert_ascii("DCX\0")
        br.assert_int32(0x10000)
        br.assert_int32(0x18)
        br.assert_int32(0x24)
        br.assert_int32(0x24)
        unk1 = br.read_int32()

        br.assert_ascii("DCS\0")
        uncompressed_size = br.read_int32()
        compressed_size = br.read_int32()

        br.assert_ascii("DCP\0")
        br.assert_ascii("EDGE")
        br.assert_int32(0x20)
        br.assert_int32(0x9000000)
        br.assert_int32(0x10000)
        br.assert_int32(0x0)
        br.assert_int32(0x0)
        br.assert_int32(0x00100100)

        dca_start = br.position
        br.assert_ascii("DCA\0")
        dca_size = br.read_int32()

        br.assert_ascii("EgdT")
        br.assert_int32(0x00010100)
        br.assert_int32(0x24)
        br.assert_int32(0x10)
        br.assert_int32(0x10000)

        trailing_uncompressed_size = br.assert_int32(uncompressed_size % 0x10000, 0x10000)
        egdt_size = br.read_int32()
        chunk_count = br.read_int32()
        br.assert_int32(0x100000)

        if unk1 != 0x50 + chunk_count * 0x10:
            raise ValueError("Unexpected unk1 value in EDGE DCX.")
        
        if egdt_size != 0x24 + chunk_count * 0x10:
            raise ValueError("Unexpected EgdT value in EDGE DCX.")
        
        
        decompressed = bytearray(uncompressed_size)
        dcmp_stream = BytesIO(decompressed)
        for i in range(chunk_count):
            br.assert_int32(0)
            offset = br.read_int32()
            size = br.read_int32()
            compressed = br.assert_int32(0, 1) == 1

            chunk = br.get_bytes(dca_start + dca_size + offset, size)

            if compressed:
                cmp_stream = BytesIO(chunk)
                decompressed_chunk = zlib.decompress(cmp_stream.read())
                dcmp_stream.write(decompressed_chunk)
            else:
                dcmp_stream.write(chunk)
        
        return dcmp_stream.getvalue()

    @staticmethod
    def decompress_dcx_dflt(br: BinaryReaderEx, compression: CompressionType) -> bytearray:
        unk04 = 0x10000 if (compression == DCX.CompressionType.DCX_DFLT_10000_24_9 or compression == DCX.CompressionType.DCX_DFLT_10000_44_9) else 0x11000
        unk10 = 0x24 if compression == DCX.CompressionType.DCX_DFLT_10000_24_9 else 0x44
        unk14 = 0x2C if compression == DCX.CompressionType.DCX_DFLT_10000_24_9 else 0x4C
        unk30 = 8 if compression == DCX.CompressionType.DCX_DFLT_11000_44_8 else 9
        unk38 = 15 if compression == DCX.CompressionType.DCX_DFLT_11000_44_9_15 else 0

        br.assert_ascii("DCX\0")
        br.assert_int32(unk04)
        br.assert_int32(0x18)
        br.assert_int32(0x24)
        br.assert_int32(unk10)
        br.assert_int32(unk14)

        br.assert_ascii("DCS\0")
        uncompressed_size = br.read_int32()
        compressed_size = br.read_int32()

        br.assert_ascii("DCP\0")
        br.assert_ascii("DFLT")
        br.assert_int32(0x20)
        br.assert_byte(unk30)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_int32(0x0)
        br.assert_byte(unk38)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_byte(0)
        br.assert_int32(0x0)
        br.assert_int32(0x00010100)

        br.assert_ascii("DCA\0")

        compressed_header_length = br.read_int32()

        return DCX.read_zlib(br, compressed_size)

    @staticmethod
    def decompress_dcx_krak(br: BinaryReaderEx)-> bytearray:
        br.assert_ascii("DCX\0")
        br.assert_int32(0x11000)
        br.assert_int32(0x18)
        br.assert_int32(0x24)
        br.assert_int32(0x44)
        br.assert_int32(0x4C)
        br.assert_ascii("DCS\0")
        
        uncompressed_size = br.read_int32()
        compressed_size = br.read_int32()

        br.assert_ascii("DCP\0")
        br.assert_ascii("KRAK")
        br.assert_int32(0x20)
        br.assert_int32(0x6000000)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0x10100)
        br.assert_ascii("DCA\0")
        br.assert_int32(8)

        compressed = br.read_bytes(compressed_size)
        return Oodle26.decompress(compressed, uncompressed_size)
