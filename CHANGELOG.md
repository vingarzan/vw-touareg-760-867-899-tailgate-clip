# Design history

## v15 — 3D hook-side edge fillets — 2026-10-24

- Applied a nominal R0.2 mm rolling-ball fillet to exposed convex edges of the hook/support body, including across its width. Both complete versions receive this change.
- Restored the mounting plate and separately joined peg, fins and retaining clip without additional edge treatment. The previous fin-tip design is retained.
- Added an end-on width section and checks for relief at both lateral tip corners. The local rounded entrance is approximately 8.22 mm; the nominal sharp-lip reference remains 8.1 mm.
- Cleaned float32-collapsed zero-area triangles before STL export while retaining valid small-area fillet triangles. Checks require a single watertight solid, consistent winding and positive volume.
- Physical fit and printing remain unverified.

## v14 — rounded free hook tip; design-coordinate exports only — 2026-10-24

- Rounded both corners of the free tip, tangent to the bore/outer circle and cap: R0.6 outside, R0.25 inside. Applied to both complete versions and the hook gauge.
- The 34.4 mm sharp-tip envelope becomes approximately 34.17 mm overall after rounding. The 8.1 mm nominal sharp-lip clearance becomes approximately 8.20 mm locally; bore, tooth and mounting datums are retained.
- Added exported-STL arc checks at three width stations and a close-up preview.
- Removed the two pre-rotated full-clip STL exports. Standard and flat-support models are supplied in design coordinates; earlier orientations remain in history.
- Physical fit and printing remain unverified.

## v13 — separate flat-support print variant — 2026-10-24

- Added a separate full-width backing wedge from the rear underside of the base to a tangent on the outer hook curve. The standard v12 STL geometry is retained unchanged.
- Added design-orientation and flat-face-on-bed STL files. The supplied print version is rotated about 34.46° and has approximately 723 mm² of bed contact.
- Verified that all vertices lie above the support plane, the upper features are unchanged, and the measured hook mating geometry matches the gauge. Both extra meshes pass the existing manifold checks.
- Added side-section and 3D print-orientation previews. The wedge adds approximately 3.43 cm³ of material; installation clearance, slicing and physical printing remain unverified.

## v12 — rounded hook and inward-leaning fin tips — 2026-10-24

- Replaced the hook upper angled face with a smooth entry relief and the straight diagonal shoulder cuts with curved transitions. Retained the 7.7 mm clearance, 9.7 mm bore, 8.1 mm mouth and internal tooth.
- Rounded the two upper profile corners of each fin to R0.4 mm and leaned both fins 5° inward. Root positions, wall thickness and heights are retained; measured top lengths remain the unrounded construction envelopes.
- Preserved the sharp mounting base, reinforced peg and retaining latch; geometric comparisons with v11 found zero difference in those regions.
- Updated the complete models and hook gauge, added hook/fin close-ups and checks for curved shoulders, rounded fin tips and inward lean. Peg gauge remains byte-identical.
- These new rounding/lean dimensions are design choices; physical fit remains unverified.

## v11 — trim the remaining lateral base tabs — 2026-10-24

- Narrowed the hook-end front crossbar from 27.6 to 26.3 mm, removing the 0.65 mm protrusion on each side and making it flush with the mounting base. The original width remains in the measurement record.
- Fused the crossbar into the base profile before extrusion for continuous flush faces.
- Added overall-width and three exported crossbar-section checks, plus a before/after preview.
- Retained the v10 hook clearance, bore, mouth, tooth and reinforced peg.
- Physical fit remains unverified.

## v10 — measured base-to-inside hook distance — 2026-10-24

- Added owner photo 20 and the 7.7 mm perpendicular distance from the peg/fin mounting face to the nearest inside hook curve (7.8 mm in v09).
- Retained the 20 mm outer drop and 9.7 mm bore; these measurements derive a 2.6 mm hook wall, replacing the estimated 2.5 mm.
- Updated the complete clip, hook gauge and dimensioned section; the reinforced peg geometry is unchanged.
- Added exported STL measurements at three width stations for the new clearance. Physical fit remains unverified.

## v09 — flush hook supports and reinforced peg roots — 2026-10-24

- Removed the separate lateral support webs. Hook shell, solid backing and
  neck now fit within the 26.3 mm base width, removing the 0.65 mm side ledges.
  The measured 27.6 mm front crossbar is retained as a local frame feature.
- Replaced the overlapping support pieces with one extruded side profile. Its
  rear outline meets the outside hook circle at a tangent, with no stepped
  lower corners outside the hook diameter.
- Added a tapered internal peg-root collar: inner radius 0.9 mm at Z=3.25,
  expanding to the existing 2.1 mm cavity radius over 1.1 mm of height.
- Rounded the lower ends of the 1 mm peg slots to R0.5, centred at Z=3.9 mm.
  Their lowest cut is now Z=3.4 mm. Outer peg dimensions are retained.
- Updated the full part and both fit-test pieces. Added actual peg STL sections
  showing the interior material and rounded roots, and improved preview facets.
- Added checks for flush support width, tangent contact and lower circular
  exterior, eight collar sections and ten rounded-slot measurements. Existing
  hook mouth, tooth, peg diameters, fins and side-print hook-gauge checks pass.
- New physical strength and insertion-force testing is required; CAD checks
  do not establish that the reported leg breakage has been resolved.

## v08 — compact hook fit test for printing on its side — 2026-10-24

- Replaced the bulky 5 mm hook slice with a compact, 4 mm-wide hook gauge.
- Isolated its mating geometry directly from the complete clip, retaining the
  9.7 mm bore, 8.1 mm mouth and 1.4 × 1.4 mm tooth opposite the opening.
- Added a rounded external grip tab and placed the entire broad side at Z=0.
  Print size is approximately 20.92 × 14.75 × 4 mm, with 130.28 mm² of bed contact.
- Verified that the whole profile contacts the bed and remains constant through
  its height, so this gauge geometry requires no supports. No printer profile
  or physical print has been tested.
- Compared the saved test STL with the complete clip's mating region; checked
  the bore, mouth and tooth at three width stations and 51 clear entry rays.
- Added a dedicated hook-gauge print preview and instructions.
- Complete clip, its side-oriented copy and the peg test STLs are byte-identical
  to v07. This revision changes the hook test and its verification/documentation.
- The thin gauge checks fit dimensions; it does not reproduce full-width
  stiffness, spring force, retention or service life.

## v07 — 9.7 mm inside diameter — 2026-10-24

- Owner corrected the hook bore to 9.7 mm inside diameter, explicitly confirming
  diameter rather than radius. This supersedes the initial 9.4 mm cavity reading.
- Regenerated the hook shell, cut clearances, centred tooth, fit-test slice and
  previews from the corrected diameter.
- Retained the full-width solid back link and the remaining supplied dimensions.
- All four STL geometry checks, twenty solid-back sections, fifty-one entry rays
  and exported mating dimensions pass. Physical fit remains untested.

## v06 — solid back link from hook to base — 2026-10-24

- Filled the former gap behind the hook with a solid web across the full width,
  joining the inclined rear wall, upper hook and mounting base.
- Preserved the existing rear slope, overall size and flat mounting surface.
- Applied the cavity and mouth clearances after adding the solid backing,
  preserving the 8.1 mm opening and centred 1.4 × 1.4 mm tooth.
- Updated the hook fit-test slice and previews; the centre section labels the
  solid link so the filled area is visible for review.
- Added twenty exported-STL section checks at five width stations and four
  depths to detect any remaining gap. The v05 STL fails this new check as
  expected; all v06 sections pass. Existing clearance and tooth checks pass.
- All four STLs remain watertight single solids with zero degenerate triangles.
  Physical fit and print performance remain untested.

## v05 — corrected tooth size and placement — 2026-10-24

- Owner corrected the tooth dimensions from 2.4 × 2.4 mm to 1.4 × 1.4 mm.
- Centred the transverse tooth diametrically opposite the hook opening,
  with 1.4 mm inward radial projection and 1.4 mm local tangential height.
- Added exported-STL section checks at both sides and the middle to verify
  its size and zero tangential offset from the opposite-mouth diameter.
- Updated the hook fit-test slice and dimensioned section preview. The shared
  tooth/mouth diameter is drawn as a dotted line to make the placement clear.
- Retained the reopened 8.1 mm mouth, 20 mm drop from the mounting face, flat
  mounting platform, 9 mm peg-to-fin gap and continuous latch wall.
- All four STLs pass geometry validation; printing and physical fit remain untested.

## v04 — reopen the hook, add internal rib, correct height datum — 2026-10-24

- Added owner side photo 19 and used it to correct the mouth direction:
  diagonally outward, estimated at 30° above the base length axis.
- Reopened the entrance that v03's platform geometry obstructed. Clearances
  now apply to all supporting plate, frame and neck geometry, while the
  C-shaped shell defines the mating profile.
- Preserved an 8.1 mm mouth, within the owner's approximately 8–8.2 mm range.
- Added the owner's 2.4 mm-high × 2.4 mm-projecting transverse internal rib.
  The owner explicitly confirmed a raised tooth, not a recessed groove.
- Corrected the height datum to 20 mm perpendicular from the peg/fin mounting
  face down to the farthest outside hook edge. The earlier 19.8 mm span is no
  longer treated as overall height. Total model height is now 27.6 mm.
- Retained the flat mounting platform, 9 mm longitudinal peg-to-fin gap,
  asymmetric fins and continuous latch support wall.
- Updated the hook fit-test slice and added an actual exported-STL centre
  section preview with the mouth, rib and 20 mm drop dimensioned.
- Verified the exported cavity and mouth at three width stations, the rib
  at both sides and centre, and 51 unobstructed entry rays. All four STLs
  remain watertight single solids with no degenerate triangles.
- Physical fit, printing and retention remain untested. Hook angle, shell
  thickness, small radii and unmeasured absolute stations remain estimates.

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
