from io import BytesIO
from enum import Enum, IntEnum
from typing import List
from ...util.binary_reader_ex import BinaryReaderEx

class DDS:
    class DDSD(IntEnum):
        CAPS = 0x1
        HEIGHT = 0x2
        WIDTH = 0x4
        PITCH = 0x8
        PIXELFORMAT = 0x1000
        MIPMAPCOUNT = 0x20000
        LINEARSIZE = 0x80000
        DEPTH = 0x800000

    class DDPF(IntEnum):
        ALPHAPIXELS = 0x1
        ALPHA = 0x2
        FOURCC = 0x4
        RGB = 0x40
        YUV = 0x200
        LUMINANCE = 0x20000
    
    class DDSCAPS(IntEnum):
        COMPLEX = 0x8
        TEXTURE = 0x1000
        MIPMAP = 0x400000

    class DDSCAPS2(IntEnum):
        CUBEMAP = 0x200
        CUBEMAP_POSITIVEX = 0x400
        CUBEMAP_NEGATIVEX = 0x800
        CUBEMAP_POSITIVEY = 0x1000
        CUBEMAP_NEGATIVEY = 0x2000
        CUBEMAP_POSITIVEZ = 0x4000
        CUBEMAP_NEGATIVEZ = 0x8000
        VOLUME = 0x200000

    class DXGI_FORMAT(Enum):
        UNKNOWN = 1
        R32G32B32A32_TYPELESS = 2
        R32G32B32A32_FLOAT = 3
        R32G32B32A32_UINT = 4
        R32G32B32A32_SINT = 5
        R32G32B32_TYPELESS = 6
        R32G32B32_FLOAT = 7
        R32G32B32_UINT = 8
        R32G32B32_SINT = 9
        R16G16B16A16_TYPELESS = 10
        R16G16B16A16_FLOAT = 11
        R16G16B16A16_UNORM = 12
        R16G16B16A16_UINT = 13
        R16G16B16A16_SNORM = 14
        R16G16B16A16_SINT = 15
        R32G32_TYPELESS = 16
        R32G32_FLOAT = 17
        R32G32_UINT = 18
        R32G32_SINT = 19
        R32G8X24_TYPELESS = 20
        D32_FLOAT_S8X24_UINT = 21
        R32_FLOAT_X8X24_TYPELESS = 22
        X32_TYPELESS_G8X24_UINT = 23
        R10G10B10A2_TYPELESS = 24
        R10G10B10A2_UNORM = 25
        R10G10B10A2_UINT = 26
        R11G11B10_FLOAT = 27
        R8G8B8A8_TYPELESS = 28
        R8G8B8A8_UNORM = 29
        R8G8B8A8_UNORM_SRGB = 30
        R8G8B8A8_UINT = 31
        R8G8B8A8_SNORM = 32
        R8G8B8A8_SINT = 33
        R16G16_TYPELESS = 34
        R16G16_FLOAT = 35
        R16G16_UNORM = 36
        R16G16_UINT = 37
        R16G16_SNORM = 38
        R16G16_SINT = 39
        R32_TYPELESS = 40
        D32_FLOAT = 41
        R32_FLOAT = 42
        R32_UINT = 43
        R32_SINT = 44
        R24G8_TYPELESS = 45
        D24_UNORM_S8_UINT = 46
        R24_UNORM_X8_TYPELESS = 47
        X24_TYPELESS_G8_UINT = 48
        R8G8_TYPELESS = 49
        R8G8_UNORM = 50
        R8G8_UINT = 51
        R8G8_SNORM = 52
        R8G8_SINT = 53
        R16_TYPELESS = 54
        R16_FLOAT = 55
        D16_UNORM = 56
        R16_UNORM = 57
        R16_UINT = 58
        R16_SNORM = 59
        R16_SINT = 60
        R8_TYPELESS = 61
        R8_UNORM = 62
        R8_UINT = 63
        R8_SNORM = 64
        R8_SINT = 65
        A8_UNORM = 66
        R1_UNORM = 67
        R9G9B9E5_SHAREDEXP = 68
        R8G8_B8G8_UNORM = 69
        G8R8_G8B8_UNORM = 70
        BC1_TYPELESS = 71
        BC1_UNORM = 72
        BC1_UNORM_SRGB = 73
        BC2_TYPELESS = 74
        BC2_UNORM = 75
        BC2_UNORM_SRGB = 76
        BC3_TYPELESS = 77
        BC3_UNORM = 78
        BC3_UNORM_SRGB = 79
        BC4_TYPELESS = 80
        BC4_UNORM = 81
        BC4_SNORM = 82
        BC5_TYPELESS = 83
        BC5_UNORM = 84
        BC5_SNORM = 85
        B5G6R5_UNORM = 86
        B5G5R5A1_UNORM = 87
        B8G8R8A8_UNORM = 88
        B8G8R8X8_UNORM = 89
        R10G10B10_XR_BIAS_A2_UNORM = 90
        B8G8R8A8_TYPELESS = 91
        B8G8R8A8_UNORM_SRGB = 92
        B8G8R8X8_TYPELESS = 93
        B8G8R8X8_UNORM_SRGB = 94
        BC6H_TYPELESS = 95
        BC6H_UF16 = 96
        BC6H_SF16 = 97
        BC7_TYPELESS = 98
        BC7_UNORM = 99
        BC7_UNORM_SRGB = 101
        AYUV = 102
        Y410 = 103
        Y416 = 104
        NV12 = 105
        P010 = 106
        P016 = 107
        OPAQUE_420 = 109
        YUY2 = 110
        Y210 = 111
        Y216 = 112
        NV11 = 113
        AI44 = 114
        IA44 = 115
        P8 = 116
        A8P8 = 117
        B4G4R4A4_UNORM = 118
        P208 = 119
        V208 = 120
        V408 = 121
        FORCE_UINT = 122

    class DIMENSION(IntEnum):
        TEXTURE1D = 2
        TEXTURE2D = 3
        TEXTURE3D = 4

    class RESOURCE_MISC(IntEnum):
        TEXTURECUBE = 0x4

    class ALPHA_MODE(IntEnum):
        UNKNOWN = 0
        STRAIGHT = 1
        PREMULTIPLIED = 2
        OPAQUE = 3
        CUSTOM = 4


    class PIXELFORMAT:
        dw_flags: "DDS.DDPF"
        dw_four_cc: str
        dw_rgb_bit_count: int
        dw_r_bit_mask: int
        dw_g_bit_mask: int
        dw_b_bit_mask: int
        dw_a_bit_mask: int

        @classmethod
        def new(cls):
            cls.dw_four_cc = "\0\0\0\0"
            return cls()
        
        @classmethod
        def from_binary_reader(cls, br: BinaryReaderEx):
            br.assert_int32(32)
            cls.dw_flags = DDS.DDPF(br.read_uint32())
            cls.dw_four_cc = br.read_ascii(4)
            cls.dw_rgb_bit_count = br.read_int32()
            cls.dw_r_bit_mask = br.read_uint32()
            cls.dw_g_bit_mask = br.read_uint32()
            cls.dw_b_bit_mask = br.read_uint32()
            cls.dw_a_bit_mask = br.read_uint32()
            return cls()


    class HEADER_DXT10:
        dxgi_format: "DDS.DXGI_FORMAT"
        resource_dimension: "DDS.DIMENSION"
        misc_flag: "DDS.RESOURCE_MISC"
        array_size: int
        misc_flag2: "DDS.ALPHA_MODE"

        @classmethod
        def new(cls):
            cls.dxgi_format = DDS.DXGI_FORMAT.UNKNOWN
            cls.resource_dimension = DDS.DIMENSION.TEXTURE2D
            cls.array_size = 1
            cls.misc_flag2 = DDS.ALPHA_MODE.UNKNOWN
            return cls()
        
        @classmethod
        def from_binary_reader(cls, br: BinaryReaderEx):
            cls.dxgi_format = DDS.DXGI_FORMAT(br.read_uint32())
            cls.resource_dimension = DDS.DIMENSION(br.read_uint32())
            cls.misc_flag = DDS.RESOURCE_MISC(br.read_uint32())
            cls.array_size = br.read_uint32() 
            cls.misc_flag2 = DDS.ALPHA_MODE(br.read_uint32())


    dw_flags: DDSD
    dw_height: int
    dw_width: int
    dw_pitch_or_linear_size: int
    dw_depth: int
    dw_mip_map_count: int
    dw_reserved1: List[int]
    ddspf: PIXELFORMAT
    dw_caps: DDSCAPS
    dw_caps2: DDSCAPS2
    dw_caps3: int
    dw_caps4: int
    dw_reserved2: int
    header10: HEADER_DXT10

    def data_offset(self) -> int:
        return 0x94 if self.ddspf.dw_four_cc == "DX10" else 0x80
    
    @classmethod
    def new(cls):
        cls.dw_flags = DDS.DDSD.CAPS | DDS.DDSD.HEIGHT | DDS.DDSD.WIDTH | DDS.DDSD.PIXELFORMAT
        return cls()

    @classmethod
    def from_bytes(cls, bytes: bytes):
        br: BinaryReaderEx = BinaryReaderEx(False, BytesIO(bytes))

        br.assert_ascii("DDS ")
        br.assert_int32(0x7c)
        cls.dw_flags = DDS.DDSD(br.read_uint32())
        cls.dw_height = br.read_int32()
        cls.dw_width = br.read_int32()
        cls.dw_pitch_or_linear_size = br.read_int32()
        cls.dw_depth = br.read_int32()
        cls.dw_mip_map_count = br.read_int32()
        cls.dw_reserved1 = br.read_int32s(11)
        cls.ddspf = DDS.PIXELFORMAT.from_binary_reader(br)
        cls.dw_caps = DDS.DDSCAPS(br.read_uint32())
        cls.dw_caps2 = DDS.DDSCAPS2(br.read_uint32())
        cls.dw_caps3 = br.read_int32()
        cls.dw_caps4 = br.read_int32()
        cls.dw_reserved2 = br.read_int32()

        if(cls.ddspf.dw_four_cc == "DX10"):
            cls.header10 = DDS.HEADER_DXT10.from_binary_reader(br)
        else:
            cls.header10 = None

        return cls()