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

Set new values:
```
config['Model/Architecture/Dense/units'] = 128
```