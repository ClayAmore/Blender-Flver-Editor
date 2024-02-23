from sys import float_info
from itertools import chain
from typing import List, Dict
from mathutils import Vector
from .face_set import FaceSet
from .flver_header import FLVERHeader
from .buffer_layout import BufferLayout
from ..flver import FLVER
from .vertex_buffer import VertexBuffer
from ...util.util import Util
from ...util.binary_reader_ex import BinaryReaderEx

class Mesh:
    class BoundingBoxes:
        min: Vector
        max: Vector
        unk: Vector

        def __init__(self, *params):
            min = Vector((float_info.min, float_info.min, float_info.min))
            max = Vector((float_info.max, float_info.max, float_info.max))

            if len(params) == 2:
                Util.assert_params(params, BinaryReaderEx, FLVERHeader)
                br: BinaryReaderEx = params[0]
                header: FLVERHeader = params[1]

                min = br.read_vector3()
                max = br.read_vector3()
                if header.version >= 0x2001A:
                    unk = br.read_vector3()

    dynamic: int
    material_index: int
    default_bone_index: int
    bone_indices: List[int]
    face_sets: List[FaceSet]
    vertex_buffers: List[VertexBuffer]
    vertices: List[FLVER.Vertex]
    bounding_box: BoundingBoxes

    __face_set_indices: List[int]
    __vertex_buffer_indices: List[int]

    def __init__(self, *params):
        self.default_bone_index = -1
        self.bone_indices = []
        self.face_sets = []
        self.vertex_buffers = []
        self.vertices = []

        if len(params) == 2:
            Util.assert_params(params, BinaryReaderEx, FLVERHeader)
            br: BinaryReaderEx = params[0]
            header: FLVERHeader = params[1]

            self.dynamic = br.assert_byte(0, 1)
            br.assert_byte(0)
            br.assert_byte(0)
            br.assert_byte(0)

            self.material_index = br.read_int32()
            br.assert_int32(0)
            br.assert_int32(0)
            self.default_bone_index = br.read_int32()
            bone_count = br.read_int32()
            bounding_box_offset = br.read_int32()
            bone_offset = br.read_int32()
            face_set_count = br.read_int32()
            face_set_offset = br.read_int32()
            vertex_buffer_count = br.read_int32()
            vertex_buffer_offset = br.read_int32()

            if bounding_box_offset != 0:
                br.step_in(bounding_box_offset)
                self.bounding_box = Mesh.BoundingBoxes(br, header)
                br.step_out()

            self.bone_indices = br.get_int32s(bone_offset, bone_count)
            self.__face_set_indices = br.get_int32s(face_set_offset, face_set_count)
            self.__vertex_buffer_indices = br.get_int32s(vertex_buffer_offset, vertex_buffer_count)

    def take_face_sets(self, face_set_dict: Dict[int, FaceSet]):
        self.face_sets = []
        
        for i in self.__face_set_indices:
            if i not in face_set_dict.keys():
                raise RuntimeError(f"Face set not found or already taken: {i}")

            self.face_sets.append(face_set_dict[i])
            face_set_dict.pop(i)

    def take_vertex_buffers(self, vertex_buffer_dict: Dict[int, List[VertexBuffer]], layouts: List[BufferLayout]):
        self.vertex_buffers = []
        for i in self.__vertex_buffer_indices:
            if i not in vertex_buffer_dict.keys():
                raise RuntimeError(f"Vertex buffer not found or already taken: {i}")

            self.vertex_buffers.append(vertex_buffer_dict[i])
            vertex_buffer_dict.pop(i)
        
        self.__vertex_buffer_indices = None
        
        semantics = []
        for buffer in self.vertex_buffers:
            for member in layouts[buffer.layout_index]:
                if (member.semantic is not FLVER.LayoutMember.LayoutSemantic.UV
                    and member.semantic is not FLVER.LayoutMember.LayoutSemantic.TANGENT
                    and member.semantic is not FLVER.LayoutMember.LayoutSemantic.VERTEXCOLOR
                    and member.semantic is not FLVER.LayoutMember.LayoutSemantic.POSITION
                    and member.semantic is not FLVER.LayoutMember.LayoutSemantic.NORMAL):
                    if member.semantic in semantics:
                        raise RuntimeError("Unexpected semantic list.")
                    semantics.append(member.semantic)
        
        for i, buffer in enumerate(self.vertex_buffers):
            if (buffer.buffer_index & ~0x60000000) is not i:
                raise ValueError("Unexpected vertex buffer index.")
    
    def read_vertices(self, br: BinaryReaderEx, data_offset: int, layouts: List[BufferLayout], header: FLVERHeader):
        layout_members = list(chain(*layouts))
        uv_cap = len([m for m in layout_members if m.semantic == FLVER.LayoutMember.LayoutSemantic.UV])
        tan_cap = len([m for m in layout_members if m.semantic == FLVER.LayoutMember.LayoutSemantic.TANGENT])
        color_cap = len([m for m in layout_members if m.semantic == FLVER.LayoutMember.LayoutSemantic.VERTEXCOLOR])

        vertex_count = self.vertex_buffers[0].vertex_count
        self.vertices = []
        for i in range(vertex_count):
            self.vertices.append(FLVER.Vertex(uv_cap, tan_cap, color_cap))
        
        for buffer in self.vertex_buffers:
            buffer.read_buffer(br, layouts, self.vertices, data_offset, header)
            

