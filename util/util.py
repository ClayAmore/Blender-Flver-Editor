
class Util:
    class Int32:
        MAX_SIZE = 2147483647
    
    class UShort:
        MAX_VALUE = 65535

    @staticmethod
    def assert_param(p, t: type):
        if not isinstance(p, t):
            raise TypeError(f"Wrong Type: Expected {type(p)} to be {t}!")
        
    @staticmethod
    def assert_params(params, *types):
        if len(params) != len(types):
            raise IndexError(f"Params size {len(params)} is not the same as types size {len(types)}!")
        
        for i, p in enumerate(params):
            Util.assert_param(p, types[i])
    
    @staticmethod
    def has_param(p, t: type):
        return isinstance(p, t)

    @staticmethod
    def has_params(params, *types):
        if len(params) != len(types):
            raise IndexError(f"Params size {len(params)} is not the same as types size {len(types)}!")
        
        has_params: bool = True
        for i, p in enumerate(params):
            t: type = types[i]
            if not Util.has_param(p, t):
                has_params = False
        return has_params
