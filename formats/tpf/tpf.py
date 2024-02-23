from enum import IntEnum
from typing import List
from .dds import DDS
from ..dcx import DCX
from ...util.binary_reader_ex import BinaryReaderEx


class TPF:
    class TexType(IntEnum):
        Texture = 0
        Cubemap = 1
        Volume = 2

    class TPFPlatform(IntEnum):
        PC = 0
        Xbox360 = 1
        PS3 = 2
        PS4 = 4
        Xbone = 5


    class TexHeader:
        width: int
        height: int
        texture_count: int
        unk1: int
        unk2: int
        dxgi_format: int

    class FloatStruct:
        unk00: int
        values: List[float]

        @classmethod
        def new(cls):
            cls.values = []
            return cls()

        @classmethod
        def from_binary_reader(cls, br: BinaryReaderEx):
            cls.unk00 = br.read_int32()
            length = br.read_int32()

            if length < 0 or (length % 4 is not 0):
                raise ValueError(f"Unexpected FloatStruct length: {length}")

            cls.values = [br.read_singles(length/4)]
            return cls()

    class Texture:
        name: str
        format: int
        type: "TPF.TexType"
        mip_maps: int
        flags1: int
        bytes: bytearray
        header: "TPF.TexHeader"
        float_struct : "TPF.FloatStruct"

        @classmethod
        def new(cls):
            cls.name = "Unnamed"
            cls.bytes = bytearray()
            return cls()

        @classmethod
        def new_with_values(cls, name: str, format: int, flags1: int, bytes: bytearray):
            cls.name = name
            cls.format = format
            cls.flags1 = flags1
            cls.bytes = bytes
            
            dds = DDS.from_bytes(bytes)
            if dds.dw_caps2 == DDS.DDSCAPS2:
                cls.type = TPF.TexType.Cubemap
            elif dds.dw_caps2 == DDS.DDSCAPS2.VOLUME:
                cls.type = TPF.TexType.Volume
            else:
                cls.type = TPF.TexType.Texture
            cls.mip_maps = dds.dw_mip_map_count
            return cls()
        
        @classmethod
        def from_binary_reader(cls, br: BinaryReaderEx, platform: "TPF.TPFPlatform", flag2: int, encoding: int):
            file_offset = br.read_uint32()
            file_size = br.read_int32()

            cls.format = br.read_byte()
            cls.type = TPF.TexType(br.read_byte())
            cls.mip_maps = br.read_byte()
            cls.flags1 = br.assert_byte(0, 1, 2, 3)

            if platform is not TPF.TPFPlatform.PC:
                cls.header = TPF.TexHeader()
                cls.header.width = br.read_int16()
                cls.header.height = br.read_int16()

                if platform == TPF.TPFPlatform.Xbox360:
                    br.assert_int32(0)
                elif platform == TPF.TPFPlatform.PS3:
                    cls.header.unk1 = br.read_int32()
                    if flag2 is not 0:
                        cls.header.unk2 = br.assert_int32(0, 0x69E0, 0xAAE4)
                elif (platform == TPF.TPFPlatform.PS4 or platform == TPF.TPFPlatform.Xbone):
                    cls.header.texture_count = br.assert_int32(1, 6)
                    cls.header.unk2 = br.assert_int32(0xD)

            name_offset = br.read_uint32()
            has_float_struct = br.assert_int32(0, 1) == 1

            if (platform == TPF.TPFPlatform.PS4 or platform == TPF.TPFPlatform.Xbone):
                cls.header.dxgi_format = br.read_int32()
            
            if has_float_struct:
                cls.float_struct = TPF.FloatStruct.from_binary_reader(br)

            cls.bytes = br.get_bytes(file_offset, file_size)

            if cls.flags1 == 2 or cls.flags1 == 3:
                compression_type = DCX.CompressionType.UNKOWN
                cls.bytes = DCX.decompress(cls.bytes, compression_type)
                if(compression_type is not DCX.CompressionType.DCP_EDGE):
                    raise NotImplementedError(f"TPF compression is expected to be DCP_EDGE, but it was {cls.type}")

            if encoding == 1:
                cls.name = br.get_utf16(name_offset)
            elif encoding == 0 or encoding == 2:
                cls.name = br.get_shit_jis(name_offset)

            return cls()