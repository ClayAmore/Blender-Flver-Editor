from typing import List
from enum import Enum, IntEnum
from queue import Queue
from mathutils import Vector, Color
from ..util.util import Util
from ..util.binary_reader_ex import BinaryReaderEx

class FLVER:
    class Dummy:
        position: Vector
        forward: Vector
        upward: Vector
        reference_id: int
        parent_bone_index: int
        attach_bone_index: int
        color: Vector
        flag1: bool
        use_upward_vector: bool
        unk30: int
        unk34: int

        def __init__(self, *args):
            self.parent_bone_index = -1
            self.attach_bone_index = -1

            if (len(args) == 2 and isinstance(args[0], BinaryReaderEx) and isinstance(args[1], int)):
                br: BinaryReaderEx = args[0]
                version: int = args[1]

                self.position = br.read_vector3()
                self.color = br.read_bgra() if version == 0x20010 else br.read_arbg()
                self.forward = br.read_vector3()
                self.reference_id = br.read_int16()
                self.parent_bone_index = br.read_int16()
                self.upward = br.read_vector3()
                self.attach_bone_index = br.read_int16()
                self.flag1 = br.read_boolean()
                self.use_upward_vector = br.read_boolean()
                self.unk30 = br.read_int32()
                self.unk34 = br.read_int32()
                br.assert_int32(0)
                br.assert_int32(0)

        def __str__(self):
            return f"{self.reference_id}"
        
        #TODO: add write method
    
    class Bone:
        name: str
        parent_index: int
        child_index: int
        next_sibling_index: int
        prev_sibling_index: int
        translation: Vector
        rotation: Vector
        scale: Vector
        bounding_box_min: Vector
        bounding_box_max: Vector
        unk3c: int

        def __init__(self, *params):
            self.name = ""
            self.parent_index = -1
            self.child_index = -1
            self.next_sibling_index = -1
            self.prev_sibling_index = -1
            self.scale = Vector((1,1,1))
        
            if len(params) == 2:
                Util.assert_params(params, BinaryReaderEx, bool)
                br:BinaryReaderEx = params[0]
                unicode: bool = params[1]

                self.translation = br.read_vector3()
                name_offset: int = br.read_int32()
                self.rotation = br.read_vector3()
                self.parent_index = br.read_int16()
                self.child_index = br.read_int16()
                self.scale = br.read_vector3()
                self.next_sibling_index = br.read_int16()
                self.prev_sibling_index = br.read_int16()
                self.bounding_box_min = br.read_vector3()
                self.unk3c = br.read_int32()
                self.bounding_box_max = br.read_vector3()
                br.assert_pattern(0x34, 0x00)

                if unicode:
                    self.name = br.get_utf16(name_offset)
                else:
                    self.name = br.get_shit_jis(name_offset)

    class VertexBoneWeights:
        __A: float
        __B: float
        __C: float
        __D: float

        length: int = 4

        def get(self, i: int) -> float:
            if i == 0:
                return self.__A
            elif i == 1:
                return self.__B
            elif i == 2:
                return self.__C
            elif i == 3:
                return self.__C
            else:
                IndexError(f"Index ({i}) was out of range. Must be non-negative and less than 4.")

        def set(self, i: int):
            if i == 0:
                self.__A = i 
            elif i == 1:
                self.__B = i 
            elif i == 2:
                self.__C = i 
            elif i == 3:
                self.__C = i 
            else:
                IndexError(f"Index ({i}) was out of range. Must be non-negative and less than 4.")

            
    class VertexBoneIndices:
        __A: float
        __B: float
        __C: float
        __D: float

        length: int = 4

        def get(self, i: int) -> float:
            if i == 0:
                return self.__A
            elif i == 1:
                return self.__B
            elif i == 2:
                return self.__C
            elif i == 3:
                return self.__C
            else:
                IndexError(f"Index ({i}) was out of range. Must be non-negative and less than 4.")

        def set(self, i: int):
            if i == 0:
                self.__A = i 
            elif i == 1:
                self.__B = i 
            elif i == 2:
                self.__C = i 
            elif i == 3:
                self.__C = i 
            else:
                IndexError(f"Index ({i}) was out of range. Must be non-negative and less than 4.")

    class VertexColor:
        A: float
        R: float
        G: float
        B: float

        def __init__(self, *arbg):
            if arbg:
                if isinstance(arbg[0], float):
                    self.A = arbg[0]
                    self.R = arbg[1]
                    self.G = arbg[2]
                    self.B = arbg[3]
                elif isinstance(arbg[0], int):
                    self.A = float(arbg[0])/255.0
                    self.R = float(arbg[1])/255.0
                    self.G = float(arbg[2])/255.0
                    self.B = float(arbg[3])/255.0
        
        @classmethod
        def read_float_rgba(cls, br: BinaryReaderEx):
            r = br.read_single()
            g = br.read_single()
            b = br.read_single()
            a = br.read_single()
            return cls(a, r, g, b)
        
        @classmethod
        def read_float_argb(cls, br: BinaryReaderEx):
            a = br.read_single()
            r = br.read_single()
            g = br.read_single()
            b = br.read_single()
            return cls(a, r, g, b)
        
        @classmethod
        def read_byte_rgba(cls, br: BinaryReaderEx):
            a = br.read_byte()
            r = br.read_byte()
            g = br.read_byte()
            b = br.read_byte()
            return cls(a, r, g, b)


    class Vertex:
        position: Vector
        bone_weights: "FLVER.VertexBoneWeights"
        bone_indices: "FLVER.VertexBoneIndices"
        normal: Vector
        normal_w: int
        uvs: List[Vector]
        tangents: List[Vector]
        bitangent: Vector
        colors: List["FLVER.VertexColor"]

        __uv_queue: Queue
        __tangent_queue: Queue
        __color_queue: Queue

        def __init__(self, *params):
            if len(params) == 1:
                Util.assert_param(params[0], FLVER.Vertex)
                clone: FLVER.Vertex = params[0]
                self.position = clone.position
                self.bone_weights = clone.bone_weights
                self.bone_indices = clone.bone_indices
                self.normal = clone.normal
                self.uvs = clone.uvs
                self.tangents = clone.tangents
                self.bitangent = clone.bitangent
                self.colors = clone.colors

            if len(params) == 3:
                Util.assert_params(params, int, int, int)
                uv_capacity: int = params[0]
                tangent_capacity: int = params[1]
                color_capacity: int = params[2]

                self.uvs = []
                self.tangents = []
                self.colors = []
        
        def read(self, br: BinaryReaderEx, layout: List, uv_factor: float):
            layout: List[FLVER.LayoutMember] = layout
            for member in layout:
                if member.semantic == FLVER.LayoutMember.LayoutSemantic.POSITION:
                    if member.type == FLVER.LayoutMember.LayoutType.FLOAT3:
                        self.position = br.read_vector3()
                    elif member.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                        self.position = br.read_vector3()
                        br.assert_single()
                    elif member.type == FLVER.LayoutMember.LayoutType.EDGECOMPRESSED:
                        sad = True
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                
                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.BONEWEIGHTS:
                    if member.type == FLVER.LayoutMember.LayoutType.BYTE4A:
                        for i in range(4):
                            self.bone_weights[i] = br.read_s_byte() / 127.0
                    elif member.type == FLVER.LayoutMember.LayoutType.BYTE4C:
                        for i in range(4):
                            self.bone_weights[i] = br.read_byte() / 255.0
                    elif (member.type == FLVER.LayoutMember.LayoutType.UVPAIR
                            or member.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4A):
                        for i in range(4):
                            self.bone_weights[i] = br.read_int16() / 32767.0
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                
                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.BONEINDICES:
                    if member.type == FLVER.LayoutMember.LayoutType.BYTE4B:
                        for i in range(4):
                            self.bone_indices[i] = br.read_byte()
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORTBONEINDICES:
                        for i in range(4):
                            self.bone_indices[i] = br.read_uint16()
                    elif member.type == FLVER.LayoutMember.LayoutType.BYTE4E:
                        for i in range(4):
                            self.bone_indices[i] = br.read_byte()
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                
                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.NORMAL:
                    if member.type == FLVER.LayoutMember.LayoutType.FLOAT3:
                        self.normal = br.read_vector3()
                    elif member.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                        self.normal = br.read_vector3()
                        w = br.read_single()
                        self.normal_w = int(w)
                        if w != self.normal_w:
                            raise ValueError(f"Float4 Normal W was not a whole number: {w}")
                    elif (member.type == FLVER.LayoutMember.LayoutType.BYTE4A
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4B
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4C
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4E):
                        self.normal = self.read_byte_norm_xyz(br)
                        self.normal_w = br.read_byte()
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORT2TOFLOAT2:
                        self.normal_w = br.read_byte()
                        self.normal = self.read_byte_norm_zyx(br)
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4A:
                        self.normal = self.read_short_norm_xyz(br)
                        self.normal_w = br.read_int16()
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4B:
                        self.normal = self.read_ushort_norm_xyz(br)
                        self.normal_w = br.read_int16()
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                    
                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.UV:
                    if member.type == FLVER.LayoutMember.LayoutType.FLOAT2:
                        v = br.read_vector2()
                        self.uvs.append(Vector((v[0], v[1], 0)))
                    elif member.type == FLVER.LayoutMember.LayoutType.FLOAT3:
                        self.uvs.append(br.read_vector3())
                    elif member.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                        v = br.read_vector2()
                        self.uvs.append(Vector((v[0], v[1], 0)))
                        self.uvs.append(Vector((v[0], v[1], 0)))
                    elif (member.type == FLVER.LayoutMember.LayoutType.BYTE4A
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4B
                          or member.type == FLVER.LayoutMember.LayoutType.SHORT2TOFLOAT2
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4C
                          or member.type == FLVER.LayoutMember.LayoutType.UV
                          ):
                        self.uvs.append(Vector((br.read_int16(), br.read_int16(), 0))/uv_factor)
                    elif member.type == FLVER.LayoutMember.LayoutType.UVPAIR:
                        self.uvs.append(Vector((br.read_int16(), br.read_int16(), 0))/ uv_factor)
                        self.uvs.append(Vector((br.read_int16(), br.read_int16(), 0))/ uv_factor)
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4B:
                        self.uvs.append(Vector((br.read_int16(), br.read_int16(), br.read_int16()))/ uv_factor)
                        br.assert_int16()
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")

                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.TANGENT:
                    if member.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                        self.tangents.append(br.read_vector4())
                    elif (member.type == FLVER.LayoutMember.LayoutType.BYTE4A
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4B
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4C
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4E
                          ):
                        self.tangents.append(self.read_byte_norm_xyzw(br))
                    elif member.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4A:
                        self.tangents.appen(self.read_short_norm_xyzw(br))
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")

                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.BITANGENT:
                    if (member.type == FLVER.LayoutMember.LayoutType.BYTE4A
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4B
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4C
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4E
                          ):
                        self.bitangent = self.read_byte_norm_xyzw(br)
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                
                elif member.semantic == FLVER.LayoutMember.LayoutSemantic.VERTEXCOLOR:
                    if member.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                        self.colors.append(FLVER.VertexColor.read_float_rgba(br))
                    elif (member.type == FLVER.LayoutMember.LayoutType.BYTE4A
                          or member.type == FLVER.LayoutMember.LayoutType.BYTE4C):
                        self.colors.append(FLVER.VertexColor.read_byte_rgba(br))
                    else:
                        raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")
                else:
                    raise NotImplementedError(f"Read not implemented for {member.type} {member.semantic}.")


        def read_byte_norm(self, br: BinaryReaderEx) -> float:
            return ((int.from_bytes(br.read_byte(), 'big' if br.big_endian else 'little') - 127) / 127.0)

        def read_byte_norm_xyz(self, br: BinaryReaderEx) -> Vector:
            return Vector((self.read_byte_norm(br), self.read_byte_norm(br), self.read_byte_norm(br)))
        
        def read_byte_norm_xyzw(self, br:BinaryReaderEx) -> Vector:
            return Vector((self.read_byte_norm(br), self.read_byte_norm(br), self.read_byte_norm(br), self.read_byte_norm(br)))

        def read_s_byte_norm(self, br: BinaryReaderEx) -> float:
            return br.read_s_byte() / 127.0

        def read_byte_norm_zyx(self, br: BinaryReaderEx) -> Vector:
            z = self.read_s_byte_norm(br)
            y = self.read_s_byte_norm(br)
            x= self.read_s_byte_norm(br)
            return Vector((x, y, z))
        
        def read_short_norm(self, br: BinaryReaderEx) -> float:
            return br.read_int16() / 32767.0
        
        def read_short_norm_xyz(self, br: BinaryReaderEx) -> Vector:
            return Vector((self.read_short_norm(br), self.read_short_norm(br), self.read_short_norm(br)))
        
        def read_short_norm_xyzw(self, br: BinaryReaderEx) -> Vector:
            return Vector((self.read_short_norm(br), self.read_short_norm(br), self.read_short_norm(br), self.read_short_norm(br)))

        def read_ushort_norm(self, br: BinaryReaderEx) -> float:
            return (br.read_uint16() - 32767) / 32767.0
        
        def read_ushort_norm_xyz(self, br: BinaryReaderEx) -> Vector:
            return Vector((self.read_ushort_norm(br), self.read_ushort_norm(br), self.read_ushort_norm(br)))



    class LayoutMember:
        class LayoutType(IntEnum):
            FLOAT2 = 0x01
            FLOAT3 = 0x02
            FLOAT4 = 0x03
            BYTE4A = 0x10
            BYTE4B = 0x11
            SHORT2TOFLOAT2 = 0x12
            BYTE4C = 0x13
            UV = 0x15
            UVPAIR = 0x16
            SHORTBONEINDICES = 0x18
            SHORT4TOFLOAT4A = 0x1A
            SHORT4TOFLOAT4B = 0x2E
            BYTE4E = 0x2F
            EDGECOMPRESSED = 0xF0

        class LayoutSemantic(IntEnum):
            POSITION = 0
            BONEWEIGHTS = 1
            BONEINDICES = 2
            NORMAL = 3
            UV = 5
            TANGENT = 6
            BITANGENT = 7
            VERTEXCOLOR = 10

        unk00: int
        type: LayoutType
        semantic: LayoutSemantic
        index: int

        def __init__(self, *params):
            self.index = 0
            self.unk00 = 0

            if len(params) == 4:
                Util.assert_params(params, FLVER.LayoutMember.LayoutType, FLVER.LayoutMember.LayoutSemantic, int, int)
                self.type = params[0]
                self.semantic = params[1]
                self.index = params[2]
                self.unk00 = params[3]

            if len(params) == 2:
                if Util.has_params(params, FLVER.LayoutMember.LayoutType, FLVER.LayoutMember.LayoutSemantic):
                    self.type = params[0]
                    self.semantic = params[1]

                elif Util.has_params(params, BinaryReaderEx, int):
                    br: BinaryReaderEx = params[0]
                    struct_offset: int = params[1]

                    self.unk00 = br.read_int32()
                    br.assert_int32(struct_offset)
                    self.type = FLVER.LayoutMember.LayoutType(br.read_uint32())
                    self.semantic = FLVER.LayoutMember.LayoutSemantic(br.read_uint32())
                    self.index = br.read_int32()
        
        def size(self):
            if self.type == FLVER.LayoutMember.LayoutType.EDGECOMPRESSED:
                return 1
            elif (self.type == FLVER.LayoutMember.LayoutType.BYTE4A or
                self.type == FLVER.LayoutMember.LayoutType.BYTE4B or
                self.type == FLVER.LayoutMember.LayoutType.SHORT2TOFLOAT2 or
                self.type == FLVER.LayoutMember.LayoutType.BYTE4C or
                self.type == FLVER.LayoutMember.LayoutType.UV or
                self.type == FLVER.LayoutMember.LayoutType.BYTE4E):
                return 4

            elif (self.type == FLVER.LayoutMember.LayoutType.FLOAT2 or
                self.type == FLVER.LayoutMember.LayoutType.UVPAIR or
                self.type == FLVER.LayoutMember.LayoutType.SHORTBONEINDICES or
                self.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4A or
                self.type == FLVER.LayoutMember.LayoutType.SHORT4TOFLOAT4B):
                return 8

            elif self.type == FLVER.LayoutMember.LayoutType.FLOAT3:
                return 12

            elif self.type == FLVER.LayoutMember.LayoutType.FLOAT4:
                return 16

            else:
                raise NotImplementedError(f"No size defined for buffer layout type: {type}");

