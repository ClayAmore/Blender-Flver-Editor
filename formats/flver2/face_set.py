from typing import List
from enum import IntFlag
from .flver_header import FLVERHeader
from ...util.util import Util
from ...util.binary_reader_ex import BinaryReaderEx

class FaceSet:
    class FSFlags(IntFlag):
        NONE = 0
        LODLEVEL1 = 0x0100_0000
        LODLEVEL2 = 0x0200_0000
        EDGECOMPRESSED = 0x4000_0000
        MOTIONBLUR = 0x8000_0000
    
    flags: FSFlags
    triangle_strip: bool
    cull_backfaces: bool
    unk06: int
    indices: List[int]
    
    def __init__(self, *params):
        self.flags = FaceSet.FSFlags.NONE
        self.triangle_strip = False
        self.cull_backfaces = True,
        self.indices = []

        if len(params) == 5:
            Util.assert_params(params, FaceSet.FSFlags, bool, bool, int, [int])
            self.flags = params[0]
            self.trianlge_strup = params[1]
            self.cull_backfaces = params[2]
            self.unk06 = params[3]
            self.indices = params[4]

        if len(params) == 4:
            Util.assert_params(params, BinaryReaderEx, FLVERHeader, int, int)
            br: BinaryReaderEx = params[0]
            header: FLVERHeader = params[1]
            header_index_size: int = params[2]
            data_offset: int = params[3]

            self.flags = FaceSet.FSFlags(br.read_uint32())
            self.triangle_strip = br.read_boolean()
            self.cull_backfaces = br.read_boolean()
            self.unk06 = br.read_int16()
            index_count = br.read_int32()
            indices_offset = br.read_int32()

            index_size = 0
            if header.version > 0x20005:
                br.read_int32()
                br.assert_int32(0)
                index_size = br.assert_int32(0, 16, 32)
                br.assert_int32(0)
            
            if index_size == 0:
                index_size = header_index_size

            if index_size == 8:
                br.step_in(data_offset + indices_offset)
                #TODO: Check if you need to implement this
                br.step_out()

            elif index_size == 16:
                self.indices = []
                for index in br.get_uint16s(data_offset + indices_offset, index_count):
                    self.indices.append(index)
            
            elif index_size == 32:
                self.indices = br.get_int32s()
            
            else:
                raise NotImplementedError(f"Unsupported index size: {index_size}")


    def triangluate(self, allow_primitive_restarts: bool, include_degenerate_faces: bool = False):
        if(self.triangle_strip):
            triangles = []
            flip = False
            for i in range(len(self.indices) - 2):
                vi1 = self.indices[i]
                vi2 = self.indices[i + 1]
                vi3 = self.indices[i + 2]

                if(allow_primitive_restarts  and (vi1 == 0xFFFF or vi2 == 0xFFFF or vi3 == 0xFFFF)):
                    flip = False
                else:
                    if include_degenerate_faces or vi1 != vi2 and vi2 != vi3 and vi3 != vi1:
                        if flip:
                            triangles.append(vi3)
                            triangles.append(vi2)
                            triangles.append(vi1)
                        else:
                            triangles.append(vi1)
                            triangles.append(vi2)
                            triangles.append(vi3)
                    
                    flip = False
                return triangles
        return self.indices.copy()
