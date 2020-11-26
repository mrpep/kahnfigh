## Kahnfigh

Load a yaml file:

```
from kahnfigh import Config
config = Config('sample.yaml')
```

Access keys using xpath syntax:

```
config['Model/Architecture/Dense/units']
```

Edit existing values:
```
config['Model/Architecture/Dense/units'] = 128
```

If the path doesn't exist, it will automatically create it:
```
config['Model/Architecture/MyNewLayer/units'] = 88
```

Moreover, you might want to find all paths matching a pattern. Use a wildcard:
```
config['Model/Architecture/*/units']
```
If there was a list in config['Model/Architecture'], then it will return all the value of key 'units' of all elements of the list which have that key

You can also do some more elaborate but handy things like:
```
config['Model/Architecture/*/[units=88]/name']
```
This will return the value of key name of all elements of the list in Architecture which have the pair key:value units:88

Sometimes it is really hard to work with nested dictionaries. Use to_shallow() and turn it into a depth-1 dictionary:
```
shallow = config.to_shallow()
```

Then, after some modifications, you might want to go back to a nested dictionary:
```
from kahnfigh.core import shallow_to_deep

nested = shallow_to_deep(shallow)
```

Also, you may want to create custom behaviours. For example, if we want a value to be replaced by a variable when the symbol $ appears, we can do:
```
config['Model/name']
# this returns: $model_name
config['Model/Architecture/ConvLayer/filters']
# this returns: $n_filters

params = {'model_name': 'CNN-LSTM',
          'n_filters': 64}
config.replace_on_symbol('$',lambda x: params[x])

config['Model/name']
#this now returns: CNN-LSTM
config['Model/Architecture/ConvLayer/filters']

#this now returns: 64
