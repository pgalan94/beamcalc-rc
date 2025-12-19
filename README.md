# beamcalc-rc
A Reinforced Concret beam solver in Python, using [AnaStruct](https://github.com/ritchie46/anaStruct)
It's a no interface version of my undergraduate thesis project, available at https://github.com/pgalan94/ImediataVigas

## Setup

```bash
pip install beamcalc-rc
```

## Example usage

Right now, the script is still "very tied" to the old (legacy) code.
I'll be refactoring this right away.
For now, checkout the `example.py` file to use this lib as intended.

## What's up

> Simply supported beams

## Up next

> All beam support types (cantilever, fixed, etc.)
> Continuous beams

## Final thoughts

Since this project uses "1-dimension finite elements approximation", I'm not planning in expanding this lib to 3d beams, like "U-shaped" balcony beams. My goal with this project is to decouple my initial script from tkinter, exposing a lib that can be used for beam solving without a GUI.
