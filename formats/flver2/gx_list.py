from sys import maxsize
from .flver_header import FLVERHeader
from ...util.util import Util
from ...util.binary_reader_ex import BinaryReaderEx

class GXList(list):
    class GXItem:
        id: str
        unk04: int
        data: bytearray

        def __init__(self, *params):
            self.id = "0"
            self.unk04 = 100
            self.data = bytearray(0)
        
            if len(params) == 3:
                Util.assert_params(params, str, int, bytearray)
                self.id = params[0]
                self.unk04 = params[1]
                self.data = params[2]
            
            if len(params) == 2:
                Util.assert_params(params, BinaryReaderEx, FLVERHeader)
                br: BinaryReaderEx = params[0]
                header: FLVERHeader = params[1]
                
                if header.version < 0x20010:
                    self.id = str(br.read_int32())
                else:
                    self.id = br.read_fixed_str(4)

                self.unk04 = br.read_int32()
                length = br.read_int32()
                self.data = bytearray(br.read_bytes(length - 0xc))


    terminator_id: int
    terminator_length: int

    def __init__(self, *params):
        self.terminator_id = Util.Int32.MAX_SIZE

        if len(params) == 2:
            Util.assert_params(params, BinaryReaderEx, FLVERHeader)
            br: BinaryReaderEx = params[0]
            header: FLVERHeader = params[1]

            if header.version < 0x20010:
                self.append(GXList.GXItem(br, header))
            else:
                id: int = br.get_int32(br.stream.tell())
                while id != Util.Int32.MAX_SIZE and id != -1:
                    self.append(GXList.GXItem(br, header))
                    id = br.get_int32(br.stream.tell())
                
                self.terminator_id = br.assert_int32(id)
                br.assert_int32(100)
                self.terminator_length = br.read_int32() - 0xc
                br.assert_pattern(self.terminator_length, 0x00)


