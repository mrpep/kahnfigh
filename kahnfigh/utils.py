import ruamel.yaml as yaml
from kahnfigh import Config

class IgnorableTag:
    def __init__(self,yaml_tag):
        self.yaml_tag = yaml_tag
        self.__name__ = yaml_tag

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.value}'.format(node))

    def __repr__(self):
        return self.value

    @classmethod
    def from_yaml(cls, constructor, node):
        return yaml.serialize(node).replace('\n...\n','').replace('\n','')

class YamlTag:
    def __init__(self,yaml_tag,special_tags=None):
        self.yaml_tag = yaml_tag
        self.__name__ = yaml_tag
        self.special_tags = special_tags

    #@classmethod
    def to_yaml(self, representer, node):
        return Config(node.value, special_tags=self.special_tags)

    #@classmethod
    def from_yaml(self, constructor, node):
        return Config(node.value, special_tags=self.special_tags)

def merge_configs(configs):
    merged_config = {}
    merged_kahnfigh = Config({})
    for config in configs:
        merged_config.update(config.to_shallow())

    for k,v in merged_config.items():
        merged_kahnfigh[k] = v

    return merged_kahnfigh

def replace_in_config(config, what, with_this):
    shallow_config = config.to_shallow()
    new_config = Config({})
    for k,v in shallow_config.items():
        if isinstance(k,str):
            k = k.replace(what,with_this)
        if isinstance(v,str):
            v = v.replace(what,with_this)
        new_config[k] = v
    return new_config



