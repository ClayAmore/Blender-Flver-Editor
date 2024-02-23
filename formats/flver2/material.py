from typing import List, Dict, get_origin
from .texture import Texture
from .flver_header import FLVERHeader
from .gx_list import GXList
from ...util.util import Util
from ...util.binary_reader_ex import BinaryReaderEx

class Material:
    name: str
    mtd: str
    flags: int
    textures: List[Texture]
    gx_index: int
    unk18: int

    __texture_index: int
    __texture_count: int

    
    def __init__(self, *params):
        self.name = ""
        self.mtd = ""
        self.textures = []
        self.gx_index = -1

        if len(params) == 3:
            Util.assert_params(params, str, str, int)
            self.name = params[0]
            self.mtd = params[1]
            self.flags = params[2]

        if len(params) == 4:
            Util.assert_params(params, BinaryReaderEx, FLVERHeader, get_origin(List[GXList]), get_origin(Dict[int, int]))
            br: BinaryReaderEx = params[0]
            header: FLVERHeader = params[1]
            gx_list: [GXList] = params[2]
            gx_list_indices: dict = params[3]

            name_offset: int = br.read_int32()
            mtd_offset: int = br.read_int32()
            self.__texture_count = br.read_int32()
            self.__texture_index = br.read_int32()
            self.flags = br.read_int32()
            gx_offset: int = br.read_int32()
            self.unk18 = br.read_int32()
            br.assert_int32(0)

            if header.unicode:
                self.name = br.get_utf16(name_offset)
                self.mtd = br.get_utf16(mtd_offset)
            else:
                self.name = br.get_shit_jis(name_offset)
                self.mtd = br.get_shit_jis(mtd_offset)

            if gx_offset == 0:
                self.gx_index = -1
            else:
                if not gx_offset in gx_list_indices.keys():
                    br.step_in(gx_offset)
                    gx_list_indices[gx_offset] = len(gx_list)
                    gx_list.append(GXList(br, header))
                    br.step_out()

                    self.gx_index = gx_list_indices[gx_offset]

    def __str__(self):
        return f"{self.name} | {self.mtd}"
    
    def take_textures(self, texture_dict: Dict[int, Texture]):
        self.textures = []
        
        for i in range(self.__texture_index, self.__texture_index + self.__texture_count):
            if i not in texture_dict.keys():
                raise RuntimeError(f"Texture not found or already taken: {i}")

            self.textures.append(texture_dict[i])
            texture_dict.pop(i)
