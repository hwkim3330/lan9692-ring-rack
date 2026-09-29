"""Connector-shaped solids, so the STL shows which way each port opens.

GitHub draws an STL in one grey, so a colour cannot say "plug goes in here" -
the geometry has to. Every side-entry connector is a body with its mouth cut
into the face it opens on; pin headers get their pins; the heatsink has fins
and the fan a bore. Sizes are the connector families' nominal openings, not any
one vendor's drawing - enough to read, not to tool from.
"""
import re

import numpy as np
import trimesh


def cube(x0, y0, z0, x1, y1, z1):
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def rod(x, y, z0, z1, d, sections=24):
    m = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=sections)
    m.apply_translation((x, y, (z0 + z1) / 2))
    return m


def cut(a, tools):
    if not tools:
        return a
    try:
        return trimesh.boolean.difference([a] + tools, engine='manifold')
    except Exception:
        return a


# mouth: (across the face, height, depth into the body, z of the mouth's bottom
#         above the PCB). None = keep the body solid.
def mouth_for(name, across, h):
    n = name.upper()
    if 'RJ45' in n:
        return [(11.7, 8.0, 14.0, 1.8)]
    if 'SFP' in n:
        return [(13.4, 8.6, 40.0, 0.6)]
    if 'MATENET' in n:
        return [(10.5, 8.5, 12.0, 2.5)]
    if 'USB-C' in n:
        return [(8.4, 2.6, 6.5, 0.3)]
    if 'USB-A' in n:
        return [(4.6, 12.0, 11.0, 1.0)] if across < 8 else [(12.0, 4.6, 11.0, 0.5)]
    if 'USB' in n:                      # micro-B
        return [(6.9, 1.9, 5.0, 0.5)]
    if 'OCULINK' in n:
        return [(18.0, 4.2, 6.0, 1.4)]
    if 'SD CARD' in n:
        return [(24.2 if across > 25 else across - 2.0, 1.4, 14.0, 0.3)]
    if 'T1S' in n or 'SPK' in n or 'SPEAKER' in n:
        return [(max(across - 2.5, 2.0), min(h - 3.0, 6.0), 8.0, 1.5)]
    if 'TE 2305987' in n:
        return [(22.0, 8.5, 12.0, 2.5)]
    return None


def terminal_holes(name, across):
    """Screw terminal: wire entries in the face, screw heads on top."""
    n = name.upper()
    if not any(k in n for k in ('CAN0', 'LIN0', 'POWER J1')):
        return 0
    return max(2, int(across // 3.5))


def side_connector(name, rect, z0, h, face):
    x0, y0, x1, y1 = rect
    body = cube(x0, y0, z0, x1, y1, z0 + h)
    along_x = face in ('-x', '+x')
    across = (y1 - y0) if along_x else (x1 - x0)
    c_across = (y0 + y1) / 2 if along_x else (x0 + x1) / 2
    tools = []
    if 'JACK' in name.upper() or 'BARREL' in name.upper():
        # barrel socket: a round bore on the axis
        d, depth = 6.4, 11.0
        zc = z0 + h / 2
        cyl = trimesh.creation.cylinder(radius=d / 2, height=depth * 2, sections=32)
        R = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0] if not along_x else [0, 1, 0])
        cyl.apply_transform(R)
        pos = {'-x': (x0, c_across, zc), '+x': (x1, c_across, zc),
               '-y': (c_across, y0, zc), '+y': (c_across, y1, zc)}[face]
        cyl.apply_translation(pos)
        return [cut(body, [cyl])]
    k = terminal_holes(name, across)
    if k:
        pitch = across / k
        for i in range(k):
            a = (y0 if along_x else x0) + pitch * (i + 0.5)
            hole = 2.4
            zb = z0 + 1.5
            if face == '-x':
                tools.append(cube(x0 - 1, a - hole / 2, zb, x0 + 5, a + hole / 2, zb + hole))
                sx = x0 + 6.0
            elif face == '+x':
                tools.append(cube(x1 - 5, a - hole / 2, zb, x1 + 1, a + hole / 2, zb + hole))
                sx = x1 - 6.0
            if face in ('-x', '+x'):
                tools.append(rod(sx, a, z0 + h - 2.5, z0 + h + 1, 2.6, 12))
            else:
                sy = y0 + 6.0 if face == '-y' else y1 - 6.0
                if face == '-y':
                    tools.append(cube(a - hole / 2, y0 - 1, zb, a + hole / 2, y0 + 5, zb + hole))
                else:
                    tools.append(cube(a - hole / 2, y1 - 5, zb, a + hole / 2, y1 + 1, zb + hole))
                tools.append(rod(a, sy, z0 + h - 2.5, z0 + h + 1, 2.6, 12))
        return [cut(body, tools)]
    for w, mh, depth, mz in (mouth_for(name, across, h) or []):
        w = min(w, across - 1.2)
        mh = min(mh, h - mz - 0.8)
        if w <= 0 or mh <= 0:
            continue
        za, zb = z0 + mz, z0 + mz + mh
        a0, a1 = c_across - w / 2, c_across + w / 2
        tools.append({
            '-x': cube(x0 - 1, a0, za, x0 + depth, a1, zb),
            '+x': cube(x1 - depth, a0, za, x1 + 1, a1, zb),
            '-y': cube(a0, y0 - 1, za, a1, y0 + depth, zb),
            '+y': cube(a0, y1 - depth, za, a1, y1 + 1, zb)}[face])
    return [cut(body, tools)]


def header(name, rect, z0, h):
    """Pin header: a 2.5 mm plastic bar and its pins. 'socket' = holes, no pins."""
    x0, y0, x1, y1 = rect
    m = re.search(r'(\d+)x(\d+)', name)
    if not m:
        return [cube(x0, y0, z0, x1, y1, z0 + h)], []
    rows, cols = sorted((int(m.group(1)), int(m.group(2))))
    long_x = (x1 - x0) >= (y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = []
    for r in range(rows):
        for c in range(cols):
            u = (c - (cols - 1) / 2) * 2.54
            v = (r - (rows - 1) / 2) * 2.54
            pts.append((cx + u, cy + v) if long_x else (cx + v, cy + u))
    if 'SOCKET' in name.upper():
        body = cube(x0, y0, z0, x1, y1, z0 + h)
        holes = [cube(px - 0.5, py - 0.5, z0 + h - 5, px + 0.5, py + 0.5, z0 + h + 1)
                 for px, py in pts]
        return [cut(body, holes)], []
    bar = cube(x0, y0, z0, x1, y1, z0 + 2.5)
    pins = [cube(px - 0.32, py - 0.32, z0 + 2.5, px + 0.32, py + 0.32, z0 + h) for px, py in pts]
    return [bar], pins


def heatsink(rect, z_top, z_bot, fins=9, base=3.0, fin_t=1.2):
    """Base against the SoM at z_top, fins hanging down to z_bot."""
    x0, y0, x1, y1 = rect
    parts = [cube(x0, y0, z_top - base, x1, y1, z_top)]
    pitch = (x1 - x0 - fin_t) / (fins - 1)
    for i in range(fins):
        fx = x0 + i * pitch
        parts.append(cube(fx, y0, z_bot, fx + fin_t, y1, z_top - base))
    return parts


def fan(cx, cy, z0, size=40.0, h=11.0, bore=37.0, pitch=32.0):
    frame = cube(cx - size / 2, cy - size / 2, z0, cx + size / 2, cy + size / 2, z0 + h)
    tools = [rod(cx, cy, z0 - 1, z0 + h + 1, bore, 48)]
    tools += [rod(cx + sx * pitch / 2, cy + sy * pitch / 2, z0 - 1, z0 + h + 1, 3.4, 12)
              for sx in (-1, 1) for sy in (-1, 1)]
    out = [cut(frame, tools), rod(cx, cy, z0 + 0.5, z0 + h - 0.5, 15.0, 32)]
    for i in range(7):                  # blades, flat, just enough to read as a fan
        a = i * 2 * np.pi / 7
        b = cube(7.0, -1.2, z0 + 3.5, 18.0, 1.2, z0 + 7.5)
        b.apply_transform(trimesh.transformations.rotation_matrix(a, [0, 0, 1], [0, 0, 0]))
        b.apply_transform(trimesh.transformations.rotation_matrix(0.35, [np.cos(a), np.sin(a), 0],
                                                                  [0, 0, z0 + 5.5]))
        b.apply_translation((cx, cy, 0))
        out.append(b)
    return out


def screw_head(x, y, z, up=True, d=5.5, hh=2.2):
    return rod(x, y, z, z + hh, d, 16) if up else rod(x, y, z - hh, z, d, 16)
