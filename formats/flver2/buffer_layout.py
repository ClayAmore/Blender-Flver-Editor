from typing import List
from ..flver import FLVER
from ...util.binary_reader_ex import BinaryReaderEx

class BufferLayout(List[FLVER.LayoutMember]):

    def __init__(self, br: BinaryReaderEx):

        if br:
            member_count: int = br.read_int32()
            br.assert_int32(0)
            test = br.stream.tell()
            br.assert_int32(0)
            member_offset: int = br.read_int32()

            br.step_in(member_offset)
            struct_offset: int = 0
            #TODO: see if not having capacity is worrysome
            for i in range(member_count):
                member = FLVER.LayoutMember(br, struct_offset)
                struct_offset += member.size()
                self.append(member)
            br.step_out()
    
    def size(self):
        size: int = 0
        for layout_member in self:
            size += layout_member.size()
        return size