## Kahnfigh

Load a yaml file:

```
import kahnfigh
config = kahnfigh.load_config('sample.yaml')
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
```
