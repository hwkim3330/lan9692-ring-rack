#!/usr/bin/env python3
"""The rack's plates as Bambu Lab A1 prints instead of laser-cut acrylic.

    python3 print_plates.py          -> print/<plate>.stl (one stack: A, B, C, C, D)

Same outline, corner columns, board holes and fan bore as the DXF (features() in rack.py), so a printed plate and
an acrylic one swap freely. PLA at 3 mm is about as stiff as 3 mm acrylic only when it is near solid, so each plate
gets a rim under its edge (outside the columns, clear of every hole) and is sliced with 40 % infill.
250 x 180 fits the A1's 256 mm bed with no brim.
"""
import os

import numpy as np
import trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union

import rack as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "print")
RIM = (3.0, 4.0)                 # width, depth under the plate
RIM_CLEAR = 3.0                  # from any hole edge


def printed_poly(kind):
    return R.plate_poly(kind)


def rim_poly(kind):
    r = R.PLATE_R
    outer = box(r, r, R.PW - r, R.PH - r).buffer(r, resolution=16)
    ring = outer.difference(outer.buffer(-RIM[0]))
    holes = unary_union([Point(x, y).buffer(d / 2 + RIM_CLEAR, resolution=24) for x, y, d in R.features(kind)])
    return ring.difference(holes)


def plate(kind):
    top = trimesh.creation.extrude_polygon(printed_poly(kind), R.T)
    rim = trimesh.creation.extrude_polygon(rim_poly(kind), RIM[1] + 0.01)
    rim.apply_translation((0, 0, -RIM[1]))
    m = trimesh.boolean.union([top, rim], engine="manifold")
    # print with the plate's top face on the bed: flat, and the rim points up
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
