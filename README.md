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