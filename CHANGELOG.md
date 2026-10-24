# Design history

## v03 — continuous latch wall and corrected spacing — 2026-10-24

- Replaced the latch's open-strut construction with a full 15 mm-wide wall
  connected to the base, with three solid curved gussets on the peg side.
- Applied the owner's approximate 9 mm longitudinal clear gap from the peg
  root edge to the nearest vertical edges of both fins. The owner explicitly
  confirmed edge-to-edge along the length, rather than a lateral or diagonal gap.
- Fin rear edges moved from X=9.5 to X=18.1 mm; the peg centre remains at X=5.4.
  The latch and frame move forward with the fins. Overall length stays 34.4 mm.
- Extended the continuous flat mounting platform to X=29.6 mm to support these
  features. The owner authorized a flat surface beneath peg and fins rather
  than reproducing material-saving recesses.
- Kept the frame foot above Z=0 so it cannot block the measured hook-mouth span.
  The extended platform now forms a flat roof over part of the hook channel.
- Updated the hook fit test to be an actual 5 mm slice of the complete hook,
  including the roof, rather than a bare circular U profile.
- Added four owner-authorized close-up photographs (15–18).
- Extended exported-STL checks to measure the 9 mm gap at both fin roots and
  confirm a continuous latch wall between reinforcement ribs at twelve sections.
- All four exported STLs pass mesh validation. Physical printing and vehicle
  fit remain unverified; wall thickness and the unmeasured absolute stations
  remain documented estimates.

## v02 — measured asymmetric fins — 2026-10-24

- Right fin: base 9.9, top 5.5, height 7.6 mm above the inner base surface.
- Left fin: base 9.5, top 6.9, height 3.7 mm above the inner base surface.
- Both fins are 1.6 mm thick, vertical on the peg side, tapering only toward the hook.
- Corrected the height datum: the taller right fin, not the peg, is the top of
  the part. Preserved the measured 19.8 mm overall height by moving the hook.
- Extended the rail foot into the ramp to avoid a trapped internal CSG pocket.
- Added a small peg fit-test STL and independent exported-STL section checks
  for the mating dimensions. All four exported meshes pass geometry checks.
- Incorporated the remaining four measurement photos with explicit owner
  permission to publish personal reference photos.
- Seller photographs are kept outside the published history at the owner's
  request; the source listing and photo URLs remain as reference links only.
- No print, slicer or vehicle fit validation. Unmeasured offsets and flexure
  geometry remain documented reconstruction assumptions.

## v01 — first reconstructed model — 2026-10-24

- Added a rebuildable measured-photo reconstruction and three STL outputs.
- Modelled the rounded rear plate, tapered hook, split mounting peg, guide fins,
  three curved spring ribs and the 15 mm transverse latch.
- Incorporated the measured 8.8/7.4 mm peg diameters and 8.5 mm total peg height,
  2.55 mm base wall, 27.6 mm frame width and 26.0 mm outside guide width.
- Added the 9.4 mm cavity / 8.1 mm mouth hook fit-test sample.
- Reloaded and validated all three STLs: watertight, one connected solid,
  consistent winding, positive volume, zero degenerate triangles.
- Guide fins in this revision are estimated and symmetric. Subsequent owner
  measurements show different left/right fins; these will form v02.
- No print, slicer or vehicle fit validation.

## Reference baseline — 2026-10-24

- Collected eight listing photographs locally and ten owner-provided photographs.
- Recorded measured spans of 34.4, 26.3, and 19.8 mm; hook cavity 9.4 mm,
  hook mouth 8.1 mm; narrow hook lip width read as 17.3 mm.
- Owner confirmed the interpretation of the two hook opening measurements.
- Established one commit per model revision, preserving generated files and
  reconstruction assumptions together.
