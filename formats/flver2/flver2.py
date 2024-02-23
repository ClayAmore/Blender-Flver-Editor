from typing import List, Dict
from mathutils import Vector
from io import BytesIO
from .flver_header import FLVERHeader
from .gx_list import GXList
from .mesh import Mesh
from .texture import Texture
from .face_set import FaceSet
from .material import Material
from .vertex_buffer import VertexBuffer
from .buffer_layout import BufferLayout
from .sekiro_unk_struct import SekiroUnkStruct
from ..flver import FLVER
from ..dcx import DCX
from ...binder.bnd4 import BND4
from ...util.sf_util import SFUtil
from ...util.binary_reader_ex import BinaryReaderEx

class FLVER2:
    
    header: FLVERHeader
    dummies: List[FLVER.Dummy]
    materials: List[Material]
    gx_lists: List[GXList]
    bones: List[FLVER.Bone]
    meshes: List[Mesh]
    buffer_layouts = List[BufferLayout]
    sekiro_unk: SekiroUnkStruct

    def __init__(self):
        self.header = FLVERHeader()
        self.dummies = []
        self.materials = []
        self.gx_lists = []
        self.bones = []
        self.meshes = []
        self.buffer_layouts = []

    def Is(self, br: BinaryReaderEx):
        if br.stream.getbuffer().nbytes < 0xc:
            return False

        magic: str = br.get_ascii(0, 6)
        endian: str = br.get_ascii(6, 2)
        br.big_endian = endian == "B\0"
        version: int = br.get_int32(8)
        return magic == "FLVER\0" and version >= 0x20000 
    
    def read_path(self, path: str):
        f = open(path, "rb")
        br = BinaryReaderEx(False, BytesIO(f.read()))
        compression: DCX.CompressionType = DCX.CompressionType.UNKOWN
        br = SFUtil.get_decompressed_br(br, compression)
        bnd = BND4()
        if(bnd.Is(br)):
            bnd.read(br)
            for f in bnd.files:
                br = BinaryReaderEx(False, BytesIO(f.bytes))
                if self.Is(br):
                    self.read(br)
        else:
            self.read(br)
            
    def read(self, br: BinaryReaderEx):
        br.set_big_endian(False)

        self.header = FLVERHeader()
        br.assert_ascii("FLVER\0")
        self.header.big_endian = br.assert_ascii("L\0", "B\0") == "B\0"
        br.set_big_endian(self.header.big_endian)

        self.header.version = br.assert_int32(0x20005, 0x20007, 0x20009, 0x2000B, 0x2000C, 0x2000D, 0x2000E, 0x2000F, 0x20010, 0x20013, 0x20014, 0x20016, 0x2001A)

        data_offset = br.read_int32()
        br.read_int32()
        dummy_count = br.read_int32()
        material_count = br.read_int32()
        bone_count = br.read_int32()
        mesh_count = br.read_int32()
        vertex_buffer_count = br.read_int32()

        self.header.bounding_box_min = br.read_vector3()
        self.header.bounding_box_max = br.read_vector3()

        br.read_int32()
        br.read_int32()

        vertex_indices_size = br.assert_byte(0, 8, 16, 32)
        self.header.unicode = br.read_boolean()
        self.header.unk4a = br.read_boolean()
        br.assert_byte(0)

        self.header.unk4c = br.read_int32()

        face_set_count = br.read_int32()
        buffer_layout_count = br.read_int32()
        texture_count = br.read_int32()

        self.header.unk5c = br.read_byte()
        self.header.unk5d = br.read_byte()
        br.assert_byte(0)
        br.assert_byte(0)

        br.assert_int32(0)
        br.assert_int32(0)
        self.header.unk68 = br.assert_int32(0, 1, 2, 3, 4)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0)
        br.assert_int32(0)

        self.dummies = []
        for i in range(dummy_count):
            self.dummies.append(FLVER.Dummy(br, self.header.version))

        self.materials = []
        gx_list_indices: Dict[int,int] = {}
        self.gx_lists: [GXList] = []
        for i in range(material_count):
            self.materials.append(Material(br, self.header, self.gx_lists, gx_list_indices))

        self.bones = []
        for i in range(bone_count):
            self.bones.append(FLVER.Bone(br, self.header.unicode))

        self.meshes = []
        for i in range(mesh_count):
            self.meshes.append(Mesh(br, self.header))

        face_sets = []
        for i in range(face_set_count):
            face_sets.append(FaceSet(br, self.header, vertex_indices_size, data_offset))

        vertex_buffers = []
        for i in range(vertex_buffer_count):
            vertex_buffers.append(VertexBuffer(br))

        self.buffer_layouts = []
        for i in range(buffer_layout_count):
            self.buffer_layouts.append(BufferLayout(br))

        textures = []
        for i in range(texture_count):
            textures.append(Texture(br, self.header))

        if self.header.version >= 0x2001A:
            self.sekiro_unk = SekiroUnkStruct(br)

        texture_dict = SFUtil.dictionize(textures)
        for material in self.materials:
            material.take_textures(texture_dict)

        if len(texture_dict) != 0:
            raise RuntimeError("Orphaned textures found.")
        
        face_set_dict = SFUtil.dictionize(face_sets)
        vertex_buffer_dict = SFUtil.dictionize(vertex_buffers)
        for mesh in self.meshes:
            mesh.take_face_sets(face_set_dict)
            mesh.take_vertex_buffers(vertex_buffer_dict, self.buffer_layouts)
            mesh.read_vertices(br, data_offset, self.buffer_layouts, self.header)
        
        if len(face_set_dict) != 0:
            raise RuntimeError("Orphaned face sets found.")
        
        if len(vertex_buffer_dict) != 0:
            raise RuntimeError("Orphaned vertex buffers found.")
        

        
        
