# VW Touareg tailgate clip — 760 867 899

Printable reconstruction from photographs and caliper measurements of the original clip.

**Status: v02 reconstructed prototype with measured, asymmetric fins. No printed fit or retention test has been performed.**

![Model preview](previews/clip.png)

## STL files

All files use millimetres. Import at 100% scale.

- [`stl/760867899_clip.stl`](stl/760867899_clip.stl): complete clip in design coordinates.
- [`stl/760867899_clip_on_side.stl`](stl/760867899_clip_on_side.stl): the same clip rotated onto one side, with its lowest surface at Z=0. Inspect supports before printing.
- [`stl/760867899_hook_fit_test.stl`](stl/760867899_hook_fit_test.stl): a 5 mm-wide sample of the hook channel. Its flat end is on the bed; print this first to check the cavity and mouth. It does not test the peg, full-width hook stiffness, or complete assembly retention.
- [`stl/760867899_peg_fit_test.stl`](stl/760867899_peg_fit_test.stl): the measured split peg on a 14 × 14 mm flat base. This is a small trial of the peg geometry, not a substitute for testing the complete clip.

The complete part has undercuts and a horizontal peg in the side orientation.
It has not been sliced or printed. Keep support material out of the four peg
slots and the spring latch where possible; inspect and clear those gaps before
attempting a fit. Do not force an undersized hook or oversized peg into the car.

## Validation and rebuilding

The exported STLs were reloaded and checked for a single connected solid,
watertightness, consistent winding, positive volume and no degenerate triangles.
See [`validation/geometry_checks.json`](validation/geometry_checks.json).
Cross-sections of the exported clip also independently verify the hook openings,
peg diameters and height, both fins, lip width and latch width to 0.003 mm of the
design values. That is a digital geometry tolerance, not a physical measurement
or printing accuracy claim.
These are geometry checks, not evidence of printed fit or service life.

The rebuildable source is provided to preserve the design history even though
only STLs are needed for printing:

```sh
python3 -m venv .venv
.venv/bin/pip install -r model/requirements.txt
.venv/bin/python model/build.py
```

[`model/parameters.json`](model/parameters.json) separates measured dimensions
from estimates. v02 incorporates the separately measured left and right fins.

Looking from the **rounded peg end toward the hook**, with the peg pointing up,
the **right fin is the taller fin** (negative Y). Both fins have a vertical edge
at the peg end and taper toward the hook. Please compare this orientation with
the original before printing the whole part.

## Reference measurements

| Feature | mm | Evidence |
|---|---:|---|
| Overall length | 34.4 | `reference/measurements/01.jpg` |
| Body width at first measurement position | 26.3 | `reference/measurements/02.jpg` |
| Overall height | 19.8 | `reference/measurements/03.jpg` |
| Hook cavity, wider interior | 9.4 | `reference/measurements/08.jpg`; interpretation confirmed by owner |
| Hook mouth, narrower entrance | 8.1 | `reference/measurements/09.jpg`; interpretation confirmed by owner |
| Narrow hook lip width | 17.3 | `reference/measurements/10.jpg`; read from jaw placement |
| Maximum frame width | 27.6 | `reference/measurements/11.jpg` |
| Outside guide width | 26.0 | `reference/measurements/12.jpg` and owner clarification |
| Base wall | 2.5–2.6 | Owner measurement; design uses midpoint 2.55 |
| Peg total height, including base wall | 8.5 | Owner measurement |
| Peg widest diameter / base diameter | 8.8 / 7.4 | Owner measurement |
| Spring latch width | 15.0 | Owner measurement |
| Right fin: base / top length | 9.9 / 5.5 | Owner measurement |
| Right fin: height above inner surface | 7.6 | Owner measurement and explicit height clarification |
| Left fin: base / top length | 9.5 / 6.9 | Owner measurement |
| Left fin: height above inner surface | 3.7 | Owner measurement |
| Both fin walls | 1.6 | Owner measurement |

The peg position, hollow centre and slits, latch positions, flexure thicknesses,
and small radii are photo estimates. Photographs do not provide a calibrated 3D scan.

The right fin reaches Z=10.15 mm above the outside base. With the 19.8 mm overall
height, the reconstructed hook reaches Z=-9.65 mm. This placement assumes the
overall height spans the tallest fin and the bottom of the hook. The circular
hook interior, its taper in width, and the unseen shoulder profile remain
reconstruction assumptions. The guide and peg locations should be checked
against a printed sample; these positions have not been directly measured.

## First print

1. Print the hook and peg fit-test pieces at 100% scale. The peg piece sits flat
   with the peg upright; the hook piece stands on its flat 5 mm-wide end.
2. Compare the full clip preview with the original, especially the tall-fin side.
3. Inspect support placement and layer paths for the full clip. The side STL is
   an orientation option, not a validated print profile. Its small contact area
   may need a brim, and its horizontal peg and fins may need support.
4. Check fit gently, then inspect for cracking and adequate retention before
   using it to hold tailgate trim. A fit-test pass does not establish service life.

Printer, material, shrinkage, temperature resistance and spring fatigue have not
been validated. No material-specific printer settings are supplied.

## Revision policy

Commit every model revision with its STL files, source parameters, preview, checks,
and change notes. Keep stable filenames for the current files; Git history retains
all prior revisions. Do not squash or overwrite the design history.

## Photographs

- `reference/measurements/`: fourteen owner-provided JPEG references, in received
  order, published with the owner's explicit permission. Camera metadata was
  removed before inclusion. Photos 13 and 14 show the same measurement view.
- `reference/listing/source.txt`: the public product listing and original photo
  links, for provenance only. The seller's photographs are **not redistributed**
  in this repository, including in its published Git history.

VW and Touareg identify the part reference only. This project is not an OEM CAD
release or a certified replacement.
