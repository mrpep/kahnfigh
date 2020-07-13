from .core import get_path, set_path, delete_path,get_config, save_config, deep_to_shallow, recursive_replace, find_path
from collections.abc import MutableMapping
from pathlib import Path

class Config(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""
    def __init__(self, path, special_tags=None):
        if isinstance(path,str):
            self.store = get_config(path,special_tags=special_tags)
        elif isinstance(path,Path):
            self.store = get_config(str(path.absolute()),special_tags=special_tags)
        elif isinstance(path,dict):
            self.store = path
        else:
            raise Exception('Invalid arg for Config')

    def __getitem__(self, key):
        if key not in self.store and '/' in key:
            results = get_path(self.store,key)
            if len(results) == 1:
                return results[0]
            elif len(results) == 0:
                raise KeyError('Invalid key')
            else:
                return results
        else:
            return self.store[key]

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

    def replace_on_symbol(self,symbol,replacement_fn,filter_fn=None):
        recursive_replace(self.store,symbol,replacement_fn,filter_fn)

    def find_path(self,value,mode='equals',action=None,filter_fn=None):
        return find_path(self,value,mode=mode,action=action,filter_fn=filter_fn)

def load_config(path):
    return Config(path)


