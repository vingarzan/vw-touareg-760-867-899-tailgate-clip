# VW Touareg tailgate clip — 760 867 899

Printable reconstruction from photographs and caliper measurements of the original clip.

**Status: v01 reconstructed prototype. No printed fit or retention test has been performed.**

![Model preview](previews/clip.png)

## STL files

All files use millimetres. Import at 100% scale.

- [`stl/760867899_clip.stl`](stl/760867899_clip.stl): complete clip in design coordinates.
- [`stl/760867899_clip_on_side.stl`](stl/760867899_clip_on_side.stl): the same clip rotated onto one side, with its lowest surface at Z=0. Inspect supports before printing.
- [`stl/760867899_hook_fit_test.stl`](stl/760867899_hook_fit_test.stl): a 5 mm-wide sample of the hook channel. Its flat end is on the bed; print this first to check the cavity and mouth. It does not test the peg, full-width hook stiffness, or complete assembly retention.

The complete part has undercuts and a horizontal peg in the side orientation.
It has not been sliced or printed. Keep support material out of the four peg
slots and the spring latch where possible; inspect and clear those gaps before
attempting a fit. Do not force an undersized hook or oversized peg into the car.

## Validation and rebuilding

The exported STLs were reloaded and checked for a single connected solid,
watertightness, consistent winding, positive volume and no degenerate triangles.
See [`validation/geometry_checks.json`](validation/geometry_checks.json).
These are geometry checks, not evidence of printed fit or service life.

The rebuildable source is provided to preserve the design history even though
only STLs are needed for printing:

```sh
python3 -m venv .venv
.venv/bin/pip install -r model/requirements.txt
.venv/bin/python model/build.py
```

[`model/parameters.json`](model/parameters.json) separates measured dimensions
from estimates. v01 still uses estimated symmetric guide fins; the newly supplied
individual left/right measurements are scheduled for the next revision.

## Reference measurements

| Feature | mm | Evidence |
|---|---:|---|
| Overall length | 34.4 | `reference/measurements/01.jpg` |
| Overall width | 26.3 | `reference/measurements/02.jpg` |
| Overall height | 19.8 | `reference/measurements/03.jpg` |
| Hook cavity, wider interior | 9.4 | `reference/measurements/08.jpg`; interpretation confirmed by owner |
| Hook mouth, narrower entrance | 8.1 | `reference/measurements/09.jpg`; interpretation confirmed by owner |
| Narrow hook lip width | 17.3 | `reference/measurements/10.jpg`; read from jaw placement |
| Maximum frame width | 27.6 | Additional owner photo |
| Outside guide width | 26.0 | Additional owner photo and clarification |
| Base wall | 2.5–2.6 | Owner measurement; design uses midpoint 2.55 |
| Peg total height, including base wall | 8.5 | Owner measurement |
| Peg widest diameter / base diameter | 8.8 / 7.4 | Owner measurement |
| Spring latch width | 15.0 | Owner measurement |

The peg position, hollow centre and slits, latch positions, flexure thicknesses,
and small radii are photo estimates. Photographs do not provide a calibrated 3D scan.

## Revision policy

Commit every model revision with its STL files, source parameters, preview, checks,
and change notes. Keep stable filenames for the current files; Git history retains
all prior revisions. Do not squash or overwrite the design history.

## Photographs

- `reference/measurements/`: ten owner-provided JPEG references, in received order.
- `reference/listing/`: eight product photographs from Prestige Motor Services.
  See `source.txt` for attribution and original links. These photographs remain
  the property of their respective rights holders; their inclusion is not a
  statement of a redistribution license.

VW and Touareg identify the part reference only. This project is not an OEM CAD
release or a certified replacement.
