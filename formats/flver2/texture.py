from mathutils import Vector
from .flver_header import FLVERHeader
from ...util.util import Util
from ...util.binary_reader_ex import BinaryReaderEx

class Texture:
    type: str
    path: str
    scale: Vector
    unk10: int
    unk11: int
    unk14: float
    unk18: float
    unk1c: float


    def __init__(self, *args):
        self.type = ""
        self.path = ""
        self.scale = Vector((1,1))
    
        if len(args) == 8:
            Util.assert_params(args, str, str, Vector, int, int, float, float, float)
            self.type = args[0]
            self.path = args[1]
            self.scale = args[2]
            self.unk10 = args[3]
            self.unk11 = args[4]
            self.unk14 = args[5]
            self.unk18 = args[6]
            self.unk1c = args[7]

        if len(args) == 2:
            Util.assert_params(args, BinaryReaderEx, FLVERHeader)

            br: BinaryReaderEx = args[0]
            header: FLVERHeader = args[1]

            path_offset = br.read_int32()
            type_offset = br.read_int32()
            self.scale = br.read_vector2()

            self.unk10 = br.assert_byte(0, 1 ,2)
            self.unk11 = br.read_boolean()
            br.assert_byte(0)
            br.assert_byte(0)

            self.unk14 = br.read_single()
            self.unk18 = br.read_single()
            self.unk1c = br.read_single()

            if header.unicode:
                self.type = br.get_utf16(type_offset)
                self.path = br.get_utf16(path_offset)
            else:
                self.type = br.get_shit_jis(type_offset)
                self.path = br.get_shit_jis(path_offset)

    def __str__(self):
        return f"{self.type} = {self.path}"
