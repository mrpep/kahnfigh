import ruamel.yaml as yaml
from IPython import embed

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