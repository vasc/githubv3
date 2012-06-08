def attrdict(struct={}):
    if isinstance(struct, dict):
        for k, v in struct.items():
            struct[k] = attrdict(v)
        return AttrDict(struct)
    elif isinstance(struct, list):
        for i, item in enumerate(struct):
            struct[i] = attrdict(item)
    return struct

class AttrDict(dict):
    """A dict whose items can also be accessed as member variables.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

    def __setattr__(self, key, value):
        print "fuck"
        dict.__dict__(self, key, attrdict(value))

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, attrdict(value))