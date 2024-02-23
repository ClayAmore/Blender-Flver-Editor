from .binder import Binder
from ..formats.dcx import DCX
from ..util.util import Util

class BinderFile:
    flags: Binder.FileFlags
    id: int
    name: str
    bytes: bytes
    compression_type: DCX.CompressionType

    def __init__(self, *params):
        self.flags = Binder.FileFlags.FLAG1
        self.id = -1
        self.name = None
        self.bytes = b''
        self.compression_type = DCX.CompressionType.ZLIB

        if params:
            Util.assert_params(params, Binder.FileFlags, int, str, bytes)
            self.flags = params[0]
            self.id = params[1]
            self.name = params[2]
            self.bytes = params[3]

    def __str__(self):
        return f"Flags 0x{self.flags.to_bytes(1, byteorder='big'):X2} | ID: {self.id} | Name: {self.name} | Length : {len(self.bytes)}"