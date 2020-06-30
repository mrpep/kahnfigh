import dpath.util
import re
from functools import reduce
import operator
from ruamel.yaml import YAML
from pathlib import Path
from IPython import embed

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
    dpaths_list = dpath.util.search(config,dpath_path,yielded=True)
    for dpath_i in dpaths_list:
        path_parts = dpath_i[0].split('/')
        nested_delete(config,path_parts)

def get_config(filename):
    yaml = YAML(typ='safe')
    config = yaml.load(Path(filename))
    return config

def save_config(dictionary,filename):
    yaml = YAML(typ='safe')
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
        all_paths.update({path_i[0]: path_i[1] for path_i in found_paths if is_leaf_elem(path_i[1])})
        if len(found_paths) > 0:
            wildpath = wildpath + '/*'
        else:
            nested_levels = False

    return all_paths

def recursive_replace(tree,symbol_to_replace,replace_func):
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