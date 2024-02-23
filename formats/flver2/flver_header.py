from mathutils import Vector

class FLVERHeader:
    big_endian: bool
    version: int
    bounding_box_min: Vector
    bounding_box_max: Vector
    unicode: bool
    unk4a: bool
    unk4c: int
    unk5c: int
    unk5d: int
    unk68: int

    def __init__(self):
        self.big_endian = False
        self.version = 0x20014
        self.unicode = True
