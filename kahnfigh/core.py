import dpath.segments

def leaf(thing):
    '''
    Return True if thing is a leaf, otherwise False.
    leaf(thing) -> bool
    '''
    #leaves = (bytes, str, int, float, bool, type(None))

    #return isinstance(thing, leaves)
    leaves = (dict, list)

    return not (isinstance(thing,leaves) or type(thing).__name__ == 'Config') # or (isinstance(thing,dict) and len(thing) == 0)

dpath.segments.leaf = leaf

import dpath.util
import re
from functools import reduce
import operator
from ruamel.yaml import YAML
from pathlib import Path
from IPython import embed
from collections.abc import Iterable
import copy
import numpy as np

def extended_leaf(thing):

    leaves = (dict, list)

    return not (isinstance(thing,leaves) or type(thing).__name__ == 'Config') or (isinstance(thing,dict) and len(thing) == 0)


def parse_path_to_dpath(config,path):
    #To do: ampliar para que pueda devolver multiples matches (no elegir correct_path[0])
    access_by_kv = re.findall('\[.*?\]',path)
    for special_token in access_by_kv:
        key = special_token.split('=')[0].replace("[","")
        val = special_token.split('=')[1].replace("]","")
        path_pre = path.split(special_token)[0]
        possible_paths = list(dpath.util.search(config,'{}*/{}'.format(path_pre,key),yielded = True))
        correct_path = [path[0] for path in possible_paths if str(path[1]) == val][0]
        parent_correct = '/'.join(correct_path.split('/')[:-1])
        path = parent_correct + path.split(special_token)[1]
    return path

def get_path(config,path):
    dpath_path = parse_path_to_dpath(config,path)
    dpaths_list = dpath.util.search(config,dpath_path,yielded=True)
    results = [dpath.util.get(config,dpath_i[0]) for dpath_i in dpaths_list]

    return results

def set_path(config,path,value):
    dpath_path = parse_path_to_dpath(config,path)
    dpaths_list = list(dpath.util.search(config,dpath_path,yielded=True))

    if len(dpaths_list) == 0:
        dpath.util.new(config,path,value)
    else:
        for dpath_i in dpaths_list:
            dpath.util.set(config,dpath_i[0],value)

def nested_delete(root,items):
    items = [int(item) if item.isdigit() else item for item in items]
    parent = reduce(operator.getitem, items[:-1], root)
    operator.delitem(parent,items[-1])

def delete_path(config,path):
    dpath_path = parse_path_to_dpath(config,path)
    dpaths_list = list(dpath.util.search(config,dpath_path,yielded=True))
    for dpath_i in dpaths_list:
        path_parts = dpath_i[0].split('/')
        nested_delete(config,path_parts)

def get_config(filename, special_tags = None,safe=False):
    if safe:
      yaml = YAML(typ='safe')
    else:
      yaml = YAML(typ='unsafe')
    if special_tags:
        for tag in special_tags:
            yaml.register_class(tag)

    config = yaml.load(Path(filename))
    return config

def save_config(dictionary,filename,mode='safe'):
    if not Path(filename).parent.exists():
        Path(filename).parent.mkdir(parents=True)
    yaml = YAML(typ=mode)
    yaml.dump(dictionary,filename)

def is_leaf_elem(elem):
    if isinstance(elem,dict) or isinstance(elem,list):
        return False
    else:
        return True

def deep_to_shallow(dictionary):
    wildpath = '*'
    all_paths = {}
    nested_levels = True

    while nested_levels:
        found_paths = list(dpath.util.search(dictionary,wildpath,yielded=True))
        all_paths.update({path_i[0]: path_i[1] for path_i in found_paths if extended_leaf(path_i[1])})
        if len(found_paths) > 0:
            wildpath = wildpath + '/*'
        else:
            nested_levels = False

    return all_paths

def order_paths(dictionary,ordered_paths):
    keys = list(dictionary.keys())
    if len(keys) > 0:
        key_split = keys[0].split('/')
        for p in range(len(key_split)):
            #test_str = '/'.join(key_split[:p])
            if all([k.split('/')[:p] == key_split[:p] for k in keys]):
                common_root = '/'.join(key_split[:p])
                depth = p

        if common_root != '':
            common_root += '/'

        parents = [common_root + k.split('/')[depth] for k in keys]
        parents = list(set(parents))
        parent_dict = {k: [pk.partition(k)[2] for pk in keys if '/'.join(pk.split('/')[:depth+1])==k] for k in parents}

        for parent,children in parent_dict.items():
            if len(children) == 0 or (len(children) == 1 and children[0] == ''):
                ordered_paths.append(parent)
            elif len(children) == 1 and children[0] != '':
                ordered_paths.append(parent+children[0])
            elif len(children) > 1:
                next_level_keys = [k[1:].split('/')[0] for k in children]
                is_path_of_list = all([k.isnumeric() for k in next_level_keys])
                if is_path_of_list:
                    for i in range(len(set(next_level_keys))):
                        children_dict = {parent + k:dictionary[parent + k] for k in children if k.lstrip('/').split('/')[0] == str(i)}
                        order_paths(children_dict,ordered_paths)
                else:
                    children_dict = {parent + k:dictionary[parent + k] for k in children}
                    order_paths(children_dict,ordered_paths)

def shallow_to_deep(dictionary):
    y = {}
    ordered_paths = []
    order_paths(dictionary,ordered_paths)
    assert len(dictionary) == len(ordered_paths)

    for path in ordered_paths:
        set_path(y,path,dictionary[path])
    return y

def recursive_replace(tree,symbol_to_replace,replace_func,filter_fn):
    if isinstance(tree,dict):
        for k,v in tree.items():
            if isinstance(v,str) and v.startswith(symbol_to_replace):
                tree[k] = replace_func(v.split(symbol_to_replace)[1])
            elif isinstance(v,dict) or isinstance(v,list):
                recursive_replace(v,symbol_to_replace,replace_func)
    elif isinstance(tree,list):
        for k,v in enumerate(tree):
            if isinstance(v,str) and v.startswith(symbol_to_replace):
                tree[k] = replace_func(v.split(symbol_to_replace)[1])
            elif isinstance(v,dict) or isinstance(v,list):
                recursive_replace(v,symbol_to_replace,replace_func)

def find_path(config,value,mode='equals', action=None, filter_fn=None):
    def check(v,value):
        try:
            if v == value:
                return 1
            else:
                return 0
        except:
            return 0

    if mode == 'equals':
        keys = [k for k,v in config.to_shallow().items() if check(v,value)]
    elif mode == 'contains':
        keys = [k for k,v in config.to_shallow().items() if isinstance(v,Iterable) and value in v]
    elif mode == 'startswith':
        keys = [k for k,v in config.to_shallow().items() if isinstance(v,str) and v.startswith(value)]

    if action:
        yaml_processor = YAML()
        for key in keys:
            if action == 'remove_value':
                config.pop(key)
            elif action == 'remove_substring':
                config[key] = yaml_processor.load(config[key].replace(value,''))
            elif callable(action):
                config[key] = action(config[key])

    return keys

def numpy_to_native(dictionary, log_warns=True):
    shallow_dict = deep_to_shallow(dictionary)
    for k,v in shallow_dict.items():
        if isinstance(v,np.generic):
            shallow_dict[k] = v.item()
            if log_warns:
                print('Warning: Converting {} from {} to native python type {}. If you are saving as yaml, consider using mode=unsafe'.format(k,type(v),type(v.item())))
    modified_dict = shallow_to_deep(shallow_dict)
    return modified_dict

def shallow_to_original_keys(dictionary,keys):
    deep = shallow_to_deep(dictionary)
    new_dict = {}
    for k in keys:
        results = get_path(deep,k)
        if len(results) == 1:
            new_dict[k] = results[0]
        elif len(results) == 0:
            raise Exception('key {} not accesible'.format(k))
        elif len(results) > 1:
            raise Exception('Key {} leads to one-to-many results'.format(k))
    return new_dict