from typing import List
from .flver_header import FLVERHeader
from .buffer_layout import BufferLayout
from ..flver import FLVER
from ...util.binary_reader_ex import BinaryReaderEx

class VertexBuffer:
    layout_index: int

    vertex_size: int
    buffer_index: int
    vertex_count: int
    buffer_offset: int

    def __init__(self, param):
        if isinstance(param, int):
            self.layout_index(param)
        
        elif isinstance(param, BinaryReaderEx):
            br: BinaryReaderEx = param
            
            self.buffer_index = br.read_int32()
            self.layout_index = br.read_int32()
            self.vertex_size = br.read_int32()
            self.vertex_count = br.read_int32()
            br.assert_int32(0)
            br.assert_int32(0)
            br.read_int32()
            self.buffer_offset = br.read_int32()
    
    def read_buffer(self, br: BinaryReaderEx, layouts: List[BufferLayout], vertices: List[FLVER.Vertex], data_offset: int, header: FLVERHeader):
        layout = layouts[self.layout_index]
        if self.vertex_size is not layout.size():
            raise ValueError("Mismatched vertex buffer and buffer layout sizes.")

        br.step_in(data_offset + self.buffer_offset)
        uv_factor = 1024
        if header.version >= 0x2000F:
            uv_factor = 2048
        
        for vertice in vertices:
            vertice.read(br, layout, uv_factor)
        br.step_out()
        
        self.vertex_size = -1
        self.buffer_index = -1
        self.vertex_count = -1
        self.buffer_offset = -1

