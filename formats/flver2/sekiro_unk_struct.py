from typing import List
from ...util.binary_reader_ex import BinaryReaderEx

class SekiroUnkStruct:
    class Member:
        unk00: List[int]
        index: int

        def __init__(self, br: BinaryReaderEx):
            if br:
                self.unk00 = br.read_int16s(4)
                self.index = br.read_int32()
                br.assert_int32(0)

    members1: List[Member]
    members2: List[Member]

    def __init__(self, br: BinaryReaderEx):
        self.members1 = []
        self.members2 = []

        if br:
            count1 = br.read_int16()
            count2 = br.read_int16()
            offset1 = br.read_uint32()
            offset2 = br.read_uint32()
            br.assert_int32(0)
            br.assert_int32(0)
            br.assert_int32(0)
            br.assert_int32(0)
            br.assert_int32(0)

            br.step_in(offset1)
            for i in range(count1):
                self.members1.append(SekiroUnkStruct.Member(br))
            br.step_out()

            br.step_in(offset2)
            for i in range(count2):
                self.members2.append(SekiroUnkStruct.Member(br))
            br.step_out()

