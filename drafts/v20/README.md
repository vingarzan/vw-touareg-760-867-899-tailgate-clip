# v20 — rounded lateral edges restored

The standard and flat-backed STLs restore side-edge rounding omitted by the v19 fast drafts. Latest tapered outlines, 34.3 mm base, +2 mm retaining-clip shift and 24.5 mm outside fin-root spacing are retained. Both full parts use design coordinates.

The fast finish blends exposed lateral edges within a 0.4 mm band; it is not an exact constant-radius CAD fillet. Plate and mounting vertices are held during blending. Final mesh simplification has a 0.0005 mm tolerance; reported upper-feature volume differences are numerical (about 0.03 mm³), rather than an intended layout change. The shallow recess remains; its floor does not receive the unfinished rolling-ball fillet.

Checks: both files reload as watertight, consistently wound positive-volume meshes. Central bores measure 9.70 mm. Actual end sections confirm rounded lateral tip corners. The flat-backed version remains above its support plane and retains more than 300 mm² of flat contact. Physical printing, fit and retention remain unverified.

Reproduce each version with model/finish_side_edges.py using the corresponding drafts/v19/stl input and model/parameters.json from this snapshot. This pipeline takes seconds and avoids the unfinished whole-solid fillet calculation.
