#!/usr/bin/env python3
"""Three acrylic stacks for the LAN9692 ring, one switch at the base of each.

    python3 rack.py            checks, DXF + order zip, STL, PNG
    python3 rack.py --no-png   skip the (slow) renders

Every plate is the same 250 x 180 x 3 mm clear acrylic with the same four
corner columns, so any upper plate bolts onto any stack. What a stack carries
is which plates you stack on it - see STACKS.
"""
import math
import os
import sys
import zipfile

import numpy as np
import trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union

import boards as B
import parts3d as P3
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# plate
PW, PH, T = 300.0, 210.0, 3.0      # 250 x 180 could not give three 3-sided CAN boards plug room
PLATE_R = 6.0
COLUMN_INSET = 8.0
M3 = 3.4
COLUMN_KEEPOUT = 6.0              # M3 M/F standoff, 5.5 mm across flats, + a hand
FAN = 40.0                        # Noctua NF-A4x10 on top of B, blowing down
FAN_H = 11.0
FAN_BORE = 36.0
FAN_PITCH = 32.0
BOARD_OFF = ((PW - B.LAN9692['size'][0]) / 2, (PH - B.LAN9692['size'][1]) / 2)
FAN_C = (BOARD_OFF[0] + B.LAN_U1[0], BOARD_OFF[1] + B.LAN_U1[1])

# --------------------------------------------------------------------------
# what goes on each plate: (board, cx, cy, rot CCW)
PLATES = {
    'A-base': [('LAN9692', PW / 2, PH / 2, 0)],
    # layer 2: TC397 connector row to the back rim; the injection module turned
    # so its two RJ45s face the front rim; the S31's USB-C to the front and
    # its RJ45/USB-A to the right rim; the 9692's fan over the switch die
    'B-ecu': [('TC397', 70.0, 145.0, 0),
              ('FIM-RJ45v2', 62.0, 42.0, 90),
              ('ESP32-S31', 240.0, 45.0, 0)],
    # layer 3: the CAN board has connectors on three edges and one free one,
    # so each board turns its free edge to the middle of the plate:
    #   left   CAN/LIN/POWER front, ETH/T1S left rim, USB-C back
    #   right  CAN/LIN/POWER back,  ETH/T1S right rim, USB-C front
    #   back   CAN/LIN/POWER left,  ETH/T1S back rim,  USB-C right
    # and the front middle stays open - that is where the cables collect.
    'C-can': [('KA7-UNO', 60.0, 60.0, 90),
              ('KA7-UNO', 240.0, 60.0, 270),
              ('KA7-UNO', 150.0, 150.0, 0)],
    'D-top': [],
}
FAN_ON = {'B-ecu'}

# layer gap above each plate kind (plate top to the next plate's underside)
GAP = {'A-base': 50.0, 'B-ecu': 50.0, 'C-can': 60.0}

STACK = ['A-base', 'B-ecu', 'C-can', 'D-top']   # bottom to top
N_STACKS = 3                      # one per LAN9692 in the ring, all the same
PLUG_ROOM = 40.0                  # clear space a port needs in front of it,
                                  # or the rim if that is closer

MIN_GAP = 5.0                     # board to board, in plan
MIN_WEB = 2.5                     # acrylic between two cuts. The fan bore to its own
                                  # screw holes is 2.93, as cut and fitted in v1
MIN_AIR = 5.0                     # vertical


# --------------------------------------------------------------------------
# placement
def transform(board, cx, cy, rot):
    w, h = B.BOARDS[board]['size']
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))

    def f(x, y):
        u, v = x - w / 2, y - h / 2
        return cx + c * u - s * v, cy + s * u + c * v
    return f


FACE_ROT = {0: {}, 90: {'-x': '-y', '-y': '+x', '+x': '+y', '+y': '-x'},
            180: {'-x': '+x', '+x': '-x', '-y': '+y', '+y': '-y'},
            270: {'-x': '+y', '+y': '+x', '+x': '-y', '-y': '-x'}}


def rect(f, x0, y0, x1, y1):
    (ax, ay), (bx, by) = f(x0, y0), f(x1, y1)
    return (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))


def placed(kind):
    """-> list of dict(board, pcb, parts[(name, rect, h, face)], holes[(x,y,d)])"""
    out = []
    for board, cx, cy, rot in PLATES[kind]:
        d = B.BOARDS[board]
        f = transform(board, cx, cy, rot)
        w, h = d['size']
        parts = [(n, rect(f, x0, y0, x1, y1), ht,
                  FACE_ROT[rot].get(face, face) if face else None, src)
                 for n, x0, y0, x1, y1, ht, face, src in d['parts']]
        out.append(dict(board=board, rot=rot, pcb=rect(f, 0, 0, w, h), parts=parts,
                        under=[(n, rect(f, x0, y0, x1, y1), zt, zb)
                               for n, x0, y0, x1, y1, zt, zb in d['under']],
                        holes=[f(x, y) + (d['hole_d'],) for x, y in d['holes']],
                        f=f))
    return out


def columns():
    return [(x, y) for x in (COLUMN_INSET, PW - COLUMN_INSET)
            for y in (COLUMN_INSET, PH - COLUMN_INSET)]


def features(kind):
    """Every circle cut in a plate: (x, y, d)."""
    f = [(x, y, M3) for x, y in columns()]
    if kind in FAN_ON:
        f.append((FAN_C[0], FAN_C[1], FAN_BORE))
        f += [(FAN_C[0] + sx * FAN_PITCH / 2, FAN_C[1] + sy * FAN_PITCH / 2, M3)
              for sx in (-1, 1) for sy in (-1, 1)]
    for p in placed(kind):
        f += p['holes']
    return f


# --------------------------------------------------------------------------
# checks
def footprint(p):
    return unary_union([box(*p['pcb'])] + [box(*r) for _, r, *_ in p['parts']]
                       + [box(*r) for _, r, *_ in p['under']])


def check_plate(kind):
    rows, ports = [], []
    ps = placed(kind)
    plate = box(0, 0, PW, PH)
    keep = [Point(x, y).buffer(COLUMN_KEEPOUT) for x, y in columns()]
    fan = box(FAN_C[0] - FAN / 2, FAN_C[1] - FAN / 2, FAN_C[0] + FAN / 2,
              FAN_C[1] + FAN / 2) if kind in FAN_ON else None

    def need(label, mm, want):
        rows.append((label, mm, want, mm >= want))

    fps = [footprint(p) for p in ps]
    for i in range(len(ps)):
        name = f"{ps[i]['board']}#{i}"
        need(f'{name} inside the plate', min(
            fps[i].bounds[0], fps[i].bounds[1], PW - fps[i].bounds[2], PH - fps[i].bounds[3]), 0.0)
        need(f'{name} to the corner columns', min(fps[i].distance(k) for k in keep), 0.0)
        if fan is not None:
            need(f'{name} to the fan', fps[i].distance(fan), MIN_GAP)
        for j in range(i + 1, len(ps)):
            need(f"{name} to {ps[j]['board']}#{j}", fps[i].distance(fps[j]), MIN_GAP)
    # acrylic webs
    cuts = features(kind)
    worst = min((math.hypot(a[0] - b[0], a[1] - b[1]) - a[2] / 2 - b[2] / 2)
                for i, a in enumerate(cuts) for b in cuts[i + 1:])
    need('thinnest web between two holes', worst, MIN_WEB)
    need('thinnest web to the plate edge',
         min(min(x, y, PW - x, PH - y) - d / 2 for x, y, d in cuts), MIN_WEB)
    # ports: sweep each port's face out to the rim and see what it meets
    for i, p in enumerate(ps):
        others = [fps[j] for j in range(len(ps)) if j != i] + keep + ([fan] if fan else [])
        for n, (x0, y0, x1, y1), h, face, src in p['parts']:
            if face in (None, 'top'):
                continue
            to_rim = {'-x': x0, '+x': PW - x1, '-y': y0, '+y': PH - y1}[face]
            r = min(PLUG_ROOM, max(to_rim, 0.0))
            lane = {'-x': (x0 - r, y0, x0, y1), '+x': (x1, y0, x1 + r, y1),
                    '-y': (x0, y0 - r, x1, y0), '+y': (x0, y1, x1, y1 + r)}[face]
            if lane[2] - lane[0] <= 0 or lane[3] - lane[1] <= 0:
                blocked = False             # already at or past the rim
            else:
                blocked = any(box(*lane).intersects(o) for o in others)
            ports.append((f"{p['board']}#{i} {n}", face, to_rim, not blocked))
    return rows, ports


def vertical(kind):
    """Clearances in the layer ABOVE this plate, and under its boards."""
    rows = []
    gap = GAP.get(kind)
    for i, p in enumerate(placed(kind)):
        d = B.BOARDS[p['board']]
        top = d['standoff'] + B.PCB_T + max(h for _, _, _, _, _, h, _, _ in d['parts'])
        if gap:
            rows.append((f"{p['board']}#{i} tallest part -> plate above", gap - top, MIN_AIR))
        for n, _, _, zb in p['under']:
            rows.append((f"{p['board']}#{i} {n} -> its own plate", d['standoff'] - zb, MIN_AIR))
    if kind in FAN_ON:
        rows.append(('fan -> plate above', gap - FAN_H, MIN_AIR))
    if kind == 'A-base':
        rows.append(('LAN9692 tallest part -> fan underside',
                     gap - B.LAN9692['standoff'] - B.PCB_T - 14.0, MIN_AIR))
    return [(l, mm, w, mm >= w) for l, mm, w in rows]


def run_checks(verbose=True):
    ok = True
    for kind in PLATES:
        rows, ports = check_plate(kind)
        rows += vertical(kind)
        bad = [r for r in rows if not r[3]] + [p for p in ports if not p[3]]
        ok &= not bad
        if not verbose:
            continue
        print(f'\n{kind}: {"OK" if not bad else "FAIL"}')
        for label, mm, want, good in rows:
            print(f'    {label:52s} {mm:8.2f}  >= {want:<4}' + ('' if good else '  <-- FAIL'))
        for label, face, to_rim, clear in ports:
            print(f'    port {label:40s} {face:>3}  {to_rim:6.1f} mm to rim  '
                  + ('clear' if clear else 'BLOCKED'))
    return ok


# --------------------------------------------------------------------------
# DXF
class Dxf:
    def __init__(self):
        self.e = []

    def line(self, x1, y1, x2, y2):
        self.e.append(f"0\nLINE\n8\nCUT\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n"
                      f"11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0\n")

    def arc(self, cx, cy, r, a0, a1):
        self.e.append(f"0\nARC\n8\nCUT\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n"
                      f"40\n{r:.4f}\n50\n{a0:.4f}\n51\n{a1:.4f}\n")

    def circle(self, cx, cy, r):
        self.e.append(f"0\nCIRCLE\n8\nCUT\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n40\n{r:.4f}\n")

    def rounded_rect(self, w, h, r):
        self.line(r, 0, w - r, 0); self.line(r, h, w - r, h)
        self.line(0, r, 0, h - r); self.line(w, r, w, h - r)
        self.arc(w - r, h - r, r, 0, 90); self.arc(r, h - r, r, 90, 180)
        self.arc(r, r, r, 180, 270); self.arc(w - r, r, r, 270, 360)

    def save(self, path):
        with open(path, 'w') as f:
            f.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n"
                    "0\nSECTION\n2\nENTITIES\n" + ''.join(self.e) + "0\nENDSEC\n0\nEOF\n")


def write_dxf(kind, path):
    d = Dxf()
    d.rounded_rect(PW, PH, PLATE_R)
    for x, y, dia in features(kind):
        d.circle(x, y, dia / 2)
    d.save(path)


# --------------------------------------------------------------------------
# 3D
COL = {'plate': (170, 205, 222), 'pcb': (30, 105, 60), 'port': (235, 125, 35),
       'top': (225, 190, 60), 'part': (55, 57, 64), 'som': (40, 80, 150),
       'sink': (190, 195, 202), 'metal': (150, 155, 162), 'fan': (35, 36, 42),
       'ka7': (30, 105, 60)}


def tagged(m, c):
    m.visual.face_colors = np.tile(np.array(list(COL[c]) + [255], np.uint8), (len(m.faces), 1))
    return m


def slab(r, z0, z1, c):
    x0, y0, x1, y1 = r
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return tagged(m, c)


def post(x, y, z0, z1, d=5.5):
    m = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=6)
    m.apply_translation((x, y, (z0 + z1) / 2))
    return tagged(m, 'metal')


def plate_poly(kind):
    r = PLATE_R
    outline = box(r, r, PW - r, PH - r).buffer(r, resolution=16)
    return outline.difference(unary_union(
        [Point(x, y).buffer(d / 2, resolution=24) for x, y, d in features(kind)]))


def plate_mesh(kind, z):
    m = trimesh.creation.extrude_polygon(plate_poly(kind), T)
    m.apply_translation((0, 0, z))
    return tagged(m, 'plate')


def board_meshes(p, z_plate_top, detail=True):
    d = B.BOARDS[p['board']]
    zp = z_plate_top + d['standoff']
    top = zp + B.PCB_T
    out = [slab(p['pcb'], zp, top, 'pcb')]
    for n, r, h, face, src in p['parts']:
        if face == 'top':
            bars, pins = P3.header(n, r, top, h)
            out += [tagged(m, 'top') for m in bars] + [tagged(m, 'metal') for m in pins]
        elif face:
            out += [tagged(m, 'port') for m in P3.side_connector(n, r, top, h, face)]
        else:
            out.append(slab(r, top, top + h, 'part'))
    for n, r, zt, zb in p['under']:
        if 'heatsink' in n:
            out += [tagged(m, 'sink') for m in P3.heatsink(r, zp - zt, zp - zb)]
        else:
            out.append(slab(r, zp - zb, zp - zt, 'som'))
    for x, y, _ in p['holes']:
        out.append(post(x, y, z_plate_top, zp, d=5.0))
        out.append(tagged(P3.screw_head(x, y, top, d=4.6, hh=1.8), 'metal'))
    return out


def layer_meshes(kind, z, detail=True, fitted=None):
    """-> [(group, mesh)]; group names what the viewer can hide or tint."""
    parts = [('plate', plate_mesh(kind, z))]
    if kind in FAN_ON:
        parts += [('fan', tagged(m, 'fan')) for m in P3.fan(FAN_C[0], FAN_C[1], z + T, FAN, FAN_H)]
    for i, p in enumerate(placed(kind)):
        if fitted is None or i in fitted:
            parts += [(p['board'], m) for m in board_meshes(p, z + T)]
    return parts


def stack_parts(explode=0.0):
    """-> [(level, group, mesh)] for the whole stack, bottom to top."""
    parts, z = [], 0.0
    for lvl, kind in enumerate(STACK):
        parts += [(lvl, g, m) for g, m in layer_meshes(kind, z)]
        if kind in GAP:
            nxt = z + T + GAP[kind]
            for x, y in columns():
                parts.append((lvl, 'column', post(x, y, z + T, nxt, d=6.0)))
            z = nxt + explode
        else:
            for x, y in columns():
                parts.append((lvl, 'column', tagged(P3.screw_head(x, y, z + T), 'metal')))
    for x, y in columns():
        parts.append((0, 'column', tagged(P3.screw_head(x, y, 0.0, up=False), 'metal')))
    return parts


def stack_mesh(explode=0.0):
    return trimesh.util.concatenate([m for _, _, m in stack_parts(explode)])


def export_glb(path):
    """One node per (level, group, colour), so the viewer can explode and tint."""
    scene = trimesh.Scene()
    groups = {}
    for lvl, g, m in stack_parts():
        c = tuple(m.visual.face_colors[0][:3])
        groups.setdefault((lvl, g, c), []).append(m)
    for (lvl, g, c), ms in groups.items():
        m = trimesh.util.concatenate(ms)
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[c[0] / 255, c[1] / 255, c[2] / 255, 1.0],
            metallicFactor=0.6 if g in ('column',) else 0.0, roughnessFactor=0.55))
        scene.add_geometry(m, node_name=f'L{lvl}|{g}|{c[0]}_{c[1]}_{c[2]}',
                           geom_name=f'L{lvl}|{g}|{c[0]}_{c[1]}_{c[2]}')
    scene.export(path)


# --------------------------------------------------------------------------
def main():
    for sub in ('dxf', 'img', 'viewer'):
        os.makedirs(os.path.join(HERE, sub), exist_ok=True)
    ok = run_checks()

    print(f'\norder: {N_STACKS} stacks, 250 x 180 x 3 mm clear acrylic')
    made = []
    for kind in PLATES:
        p = os.path.join(HERE, 'dxf', f'{kind}.dxf')
        write_dxf(kind, p)
        made.append(p)
        print(f'  {kind:8s} x{N_STACKS * STACK.count(kind)}   {len(features(kind))} holes')
    print(f'  total    x{N_STACKS * len(STACK)}')
    with zipfile.ZipFile(os.path.join(HERE, 'order-dxf.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for p in made:
            info = zipfile.ZipInfo(os.path.basename(p), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, open(p, 'rb').read())

    m = stack_mesh()
    m.export(os.path.join(HERE, 'stack.stl'))
    export_glb(os.path.join(HERE, 'viewer', 'stack.glb'))
    print(f'\nstack.stl  {m.extents.round(1).tolist()} mm, {len(m.faces)} faces')

    if '--no-png' not in sys.argv:
        for kind in PLATES:
            if PLATES[kind]:
                mm = trimesh.util.concatenate([m for _, m in layer_meshes(kind, 0.0)])
                render(mm, elev=38, azim=-35).save(os.path.join(HERE, 'img', f'layer_{kind}.png'))
        render(stack_mesh(explode=45.0), elev=20, azim=-40).save(os.path.join(HERE, 'img', 'stack.png'))
        render(stack_mesh(), elev=22, azim=-40).save(os.path.join(HERE, 'img', 'stack_closed.png'))
    print('\n' + ('ALL CHECKS OK' if ok else 'SOME CHECKS FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
