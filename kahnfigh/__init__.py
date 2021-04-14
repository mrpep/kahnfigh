from .core import *
from collections.abc import MutableMapping
from pathlib import Path

class Config(MutableMapping):
    """Dictionarity with functionalities to help accessing/modifying nested elements"""
    def __init__(self, initial_value, yaml_tags=None, safe=False):
        """
        initial_value: can be a str or pathlib Path, indicating the path to a yaml file which will 
                       be opened and parsed into a dictionary. It can also be a dictionary or another
                       Config. If it is None, an empty Config will be created.
        yaml_tags:     list of yaml tags to be registered for loading a custom yaml file.
        safe:          (default=False). Indicates if safe is used when loading the yaml file.

        """
        if isinstance(initial_value,str):
            self.store = get_config(initial_value,special_tags=yaml_tags,safe=safe)
            self.yaml_path = Path(initial_value)
        elif isinstance(initial_value,Path):
            self.store = get_config(str(initial_value.absolute()),special_tags=yaml_tags,safe=safe)
            self.yaml_path = initial_value
        elif isinstance(initial_value,dict):
            self.store = initial_value
            self.yaml_path = None
        elif isinstance(initial_value,Config):
            self.store = initial_value.store
            if hasattr(initial_value,'yaml_path'):
                self.yaml_path = initial_value.yaml_path
            else:
                self.yaml_path = None
        elif initial_value is None:
            self.store = {}
            self.yaml_path = None
        else:
            raise Exception('Invalid arg for Config of type {}'.format(type(path)))

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

    def keys(self):
        """
        Returns the Config keys (at root level)
        """
        return self.store.keys()

    def all_paths(self):
        """
        Returns all the Config keys (including the nested ones)
        """
        return self.to_shallow().keys()

    def __repr__(self):
        return str(self.store)

    def save(self,path,mode='safe'):
        """
        Exports the config to a yaml file.
        path: path where to save the yaml file
        mode: can be 'safe' or None
        """
        if mode == 'safe':
            dict_to_save = numpy_to_native(self.store)
        else:
            dict_to_save = self.store
        save_config(dict_to_save,path,mode)

    def to_shallow(self):
        """
        Turns a nested Config into a shallow one (like an unnested dictionary).
        The keys are turned into paths.
        """
        return deep_to_shallow(self.store)

    def replace_on_symbol(self,symbol,replacement_dict):
        """
        Allows to replace values that start with symbol by other values as indicated by replacement_dict
        symbol: string indicating how a value should start to replace it
        replacement_dict: a dictionary whose keys are the values that should appear after the symbol and its values tell
                          the new values.

        example:
        Given a config:

            key1: '$var1'
            key2: '$var2'
            key3: '$var1'
            key4: 'hello'

        if we call

        config.replace_on_symbol('$',{'var1': 'foo', 'var2': 'says'})

        config will be

            key1: 'foo'
            key2: 'says'
            key3: 'foo'
            key4: 'hello'
        
        """

        find_path(self,symbol,mode='startswith',action=lambda x: replacement_dict[x.split(symbol)[-1].lstrip()])

    def find_path(self,str_match,mode='equals',action=None):
        """
        Finds the paths that match a given pattern.
        str_match: string to find in the config values
        mode:      can be 'equals', which will look for an exact match of the str_match,
                   can be 'contains', which will look for the str_match as a substring of any config values,
                   can be 'startswith', which will look for a config value starting with str_match
        action:    once the path is found, action is applied over the value of that path. It can be:
                   'remove_path', which will remove the found path
                   'remove_substring', which will remove str_match from the value of the found paths
                   or a callable which will take the value of the found path as argument and return the new value.
        """
        return find_path(self,str_match,mode=mode,action=action)

    def dump(self,path,format='yaml'):
        pass

    def hash(self):
        """
        Makes a hash from the config
        """
        return get_hash(self.store)
    
    def find_keys(self,key):
        """
        Finds all the keys that contain key
        """
        return find_keys(self,key)       

def load_config(path):
    return Config(path)


