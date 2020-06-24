from .core import get_path, set_path, delete_path,get_config, save_config, deep_to_shallow
from collections.abc import MutableMapping
from pathlib import Path

class Config(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""
    def __init__(self, path):
        if isinstance(path,str):
            self.store = get_config(path)
        elif isinstance(path,Path):
            self.store = get_config(str(path.absolute()))
        elif isinstance(path,dict):
            self.store = path
        else:
            raise Exception('Invalid arg for Config')

    def __getitem__(self, key):
        results = get_path(self.store,key)
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            raise Exception('Invalid key')
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
    def save(self,path):
        save_config(self.store,path)
    def to_shallow(self):
        return deep_to_shallow(self.store)

def load_config(path):
    return Config(path)


