# beamcalc-rc
A Reinforced Concret beam solver in Python, using [AnaStruct](https://github.com/ritchie46/anaStruct)
It's a no interface version of my undergraduate thesis project, available at https://github.com/pgalan94/ImediataVigas

## Setup

```bash
pip install beamcalc-rc
```

## Example usage

```
from beamcalc import Beam, ReinforcedConcreteSection

b = Beam(s=ReinforcedConcreteSection(), gap=3.00)
b.set_supports("simply")
b.set_qloads(q=-10.00)

b.solve_incrementally(nodes=20, steps=10)

b.results.M  # nodal bending array
b.results.V  # nodal shear array
b.results.d  # nodal displacement array
```