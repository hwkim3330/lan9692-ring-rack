#!/usr/bin/env python3
"""The rack's plates as Bambu Lab A1 prints instead of laser-cut acrylic.

    python3 print_plates.py          -> print/<plate>.stl (one stack: A, B, C, C, D)

Same outline, corner columns, board holes and fan bore as the DXF (features() in rack.py), so a printed plate and
an acrylic one swap freely. Flat 3 mm, nothing sticking out (the first A-base had a rim under the edge; the user wants
it flat like the acrylic). Slice at 40 % infill: the user found the first A-base sturdy enough at 40 %.
250 x 180 fits the A1's 256 mm bed with no brim.
"""
import os

import numpy as np
import trimesh

import rack as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "print")


def plate(kind):
    m = trimesh.creation.extrude_polygon(R.plate_poly(kind), R.T)
    # print with the plate's top face on the bed (the smooth side up in the rack)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation(-m.bounds[0])
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    for kind in dict.fromkeys(R.STACK):
        m = plate(kind)
        print(f"{kind:7s} {m.extents.round(1)}  watertight={m.is_watertight}  {m.volume / 1000:.0f} cm3  "
              f"holes={len(R.features(kind))}")
        m.export(os.path.join(OUT, f"{kind}.stl"))


if __name__ == "__main__":
    main()
