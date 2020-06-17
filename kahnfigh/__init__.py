from .core import get_path, set_path, get_config

class Config():
	def __init__(self,path):
		self.config = get_config(path)

	def __getitem__(self,key):
		return get_path(self.config,key)

	def __setitem__(self,key,value):
		set_path(self.config,key,value)

def load_config(path):
	return Config(path)


