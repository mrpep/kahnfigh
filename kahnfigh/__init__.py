from .core import get_path, set_path, delete_path,get_config
from collections.abc import MutableMapping

class Config(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""
    def __init__(self, path):
        self.store = get_config(path)
    def __getitem__(self, key):
        results = get_path(self.store,key)
        if len(results) == 1:
            return results[0]
        else:
            return results
    def __setitem__(self, key, value):
        set_path(self.store,key,value)
    def __delitem__(self, key):
        delete_path(self.store,key)
    def __iter__(self):
        return iter(self.store)
    def __len__(self):
        return len(self.store)
    def __keytransform__(self, key):
        return key
    def __repr__(self):
        return str(self.store)

def load_config(path):
    return Config(path)


