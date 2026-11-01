# Print audit (2026-11-01)

The rack is normally laser-cut acrylic (`order-dxf.zip`). Since 07ee2f7 the same plates can also be printed on a
Bambu Lab A1 (`print_plates.py` → `print/<plate>.stl`; the sliced files live in the `prints` repo, `lan9692-rack/`).
`stack.stl` is a display model of the whole stack (boards as blocks) and is not meant to be printed.

Rebuilt from the generators: `python3 rack.py` (checks, DXF, zip, `stack.stl`, viewer GLB, PNGs) left every tracked
file byte-identical, and `python3 print_plates.py` produced the same four plates (same volume and size) as the STLs in
`prints/lan9692-rack/`. `print/` is now gitignored: it is derived, and the published copy is in the `prints` repo.

## Printed plates

Checked with a mesh audit (trimesh + manifold3d): closed 2-manifold, overlapping shells, wall thickness by inward rays,
downward faces steeper than 55 deg, bed fit.

| Plate | Size (mm) | Holes | Manifold | Thinnest wall | Overhang > 55 deg | Thinnest web between holes / to edge | Time / PLA (README, 40 % infill) |
|---|---|---|---|---|---|---|---|
| A-base | 250 × 180 × 3 | 12 | yes, 1 shell | 3.0 mm | none (flat, top face on the bed) | 14.1 / 6.3 mm | ~2 h 19–24 m / 123–126 g |
| B-ecu | 250 × 180 × 3 | 25 | yes, 1 shell | 3.0 mm | none | **2.9** / 6.3 mm | same |
| C-can | 250 × 180 × 3 | 12 | yes, 1 shell | 3.0 mm | none | 47.7 / 6.3 mm | same |
| D-top | 250 × 180 × 3 | 4 | yes, 1 shell | 3.0 mm | none | 160.6 / 6.3 mm | same |

One stack (A, B, C, C, D) ≈ 11 h 50 m / 625 g.

- Bed: 250 × 180 fits the 256 mm bed with 3 mm to spare on the long side, so there is no room for a brim. That is the
  README's choice (no brim) and the first A-base printed fine that way.
- Holes: Ø3.4 for M3 and Ø2.9 for M2.5 (nominal +0.4). Vertical holes print ~0.1–0.2 mm small on the A1, so they end
  up ~3.2 / ~2.7: still clear for the screws and the standoff threads.
- The thinnest web (2.9 mm, between two B-ecu holes) is several perimeters wide; nothing is under 0.8 mm.

No defects found; nothing in the generators was changed.

## Still to measure

- Flatness of a printed 250 mm plate (corner lift) before stacking: the corner columns pull it flat, but a bowed plate
  tilts the boards.
- That the columns' M3 standoffs pass the printed Ø3.4 holes without drilling (first A-base: check and note here).
