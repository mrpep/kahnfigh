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
    dpaths_list = dpath.util.search(config,dpath_path,yielded=True)
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