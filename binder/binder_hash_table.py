from ..util.binary_reader_ex import BinaryReaderEx

class BinderHashTable:
    @staticmethod
    def Assert(br: BinaryReaderEx):
        br.read_int64()
        br.read_int32()
        br.assert_byte(0x10)
        br.assert_byte(8)
        br.assert_byte(8)
        br.assert_byte(0)
