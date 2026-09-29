"""Every board on the rack: outline, mounting holes, and the parts that matter.

Coordinates are millimetres from each board's bottom-left corner, top view,
y up. A part is (name, x0, y0, x1, y1, height, face, source):

    height  above the PCB's top face. Negative-z parts (under the board) are in
            UNDER instead.
    face    '-x' '+x' '-y' '+y'  the edge a cable plugs in from, or
            'top'                plugged from above (pin headers, terminal bars)
            None                 not a connector
    source  where the numbers come from. 'assumed' means the height only; no
            position here is a guess unless it says so.

Port bodies are allowed to run past the board edge - that is where they are
on the real boards (the S31's module antenna, most USB and RJ45 jacks).
"""

# --------------------------------------------------------------------------
# Microchip EV09P11A, EVB-LAN9692-LM. Outline and holes from the released
# Gerber/Excellon (tool T23, Ø3.048); parts from the pick-and-place file.
LAN9692 = dict(
    size=(213.36, 149.86), hole_d=3.4, standoff=10.0,
    holes=[(3.556, 146.304), (101.600, 146.304), (209.804, 146.304),
           (205.187, 129.330), (205.187, 71.330), (208.788, 51.816),
           (133.350, 51.562), (3.556, 24.892)],
    parts=[
        # front edge: 7 x MATEnet (TE 9-2304372-9) + 4 x SFP+ cages
        *[(f'MATEnet P{i + 1}', x - 8.875, 0.0, x + 8.875, 21.1, 13.5, '-y', 'PnP + TE drawing')
          for i, x in enumerate((11.684, 30.734, 49.784, 68.834, 87.884, 106.934, 125.984))],
        *[(f'SFP+ {c}', x - 7.25, 0.4, x + 7.25, 46.4, 9.8, '-y', 'PnP + SFP MSA')
          for c, x in zip('ABCD', (145.6, 164.6, 183.6, 202.6))],
        # rear edge
        ('RJ45 J33', 50.863, 128.436, 66.743, 149.436, 13.5, '+y', 'PnP'),
        ('USB-C J30 console', 33.262, 141.116, 42.262, 148.616 + 0.8, 3.2, '+y', 'PnP'),
        ('OCuLink J21', 107.305, 139.621, 129.305, 147.621 + 0.8, 7.0, '+y', 'PnP, height assumed'),
        ('12 V jack J23', 166.783, 133.457, 175.783, 147.957 + 1.9, 11.0, '+y', 'PnP + PJ-002BH'),
        ('switch SW3', 182.110, 136.767, 194.110, 142.767, 6.0, '+y', 'PnP, height assumed'),
        ('reset SW2', 18.844, 142.018, 24.844, 146.018, 4.0, '+y', 'PnP, height assumed'),
        # interior
        ('expansion J4 2x20 (5V on pins 2, 4)', 202.65, 74.93, 207.73, 125.73, 5.84, 'top', 'PnP'),
        ('switch U1', 158.81, 70.19, 175.81, 87.19, 2.5, None, 'PnP'),
        ('DC-DC U3', 139.068, 115.08, 164.068, 140.08, 14.0, None, 'PnP, height assumed'),
        ('DC-DC U14', 147.61, 95.27, 172.61, 120.27, 14.0, None, 'PnP, height assumed'),
        ('DC-DC U10', 162.38, 89.95, 187.38, 114.95, 14.0, None, 'PnP, height assumed'),
        ('DC-DC U20', 85.44, 106.34, 105.44, 126.34, 14.0, None, 'PnP, height assumed'),
        ('DC-DC U17', 17.93, 78.43, 37.93, 98.43, 14.0, None, 'PnP, height assumed'),
        ('cap C324', 186.008, 121.921, 196.308, 132.221, 10.2, None, 'PnP'),
    ],
    under=[],
)
LAN_U1 = (167.31, 78.69)          # switch die centre, PnP. The fan is bored over it.

# --------------------------------------------------------------------------
# Infineon AURIX Application Kit TC3X7 V2.0. Holes from figure 7-8 of the
# Application Kit Manual; connector spans read off figure 2-2 (top placement)
# at 5.37 px/mm against the 100 mm outline - good to about ±0.5 mm.
TC397 = dict(
    size=(100.0, 100.0), hole_d=3.4, standoff=8.0,
    holes=[(11.0, 4.0), (89.0, 4.0), (96.99, 59.0), (16.0, 82.0)],
    parts=[
        ('POWER X101 barrel', 0.6, 84.2, 11.7, 100.8, 11.0, '+y', 'manual fig 2-2'),
        ('LIN X203 2x5', 15.8, 93.5, 27.6, 98.7, 8.5, 'top', 'manual fig 2-2'),
        ('CAN X202 2x5', 34.4, 93.5, 45.6, 98.7, 8.5, 'top', 'manual fig 2-2'),
        ('SD card X205', 51.2, 84.2, 65.7, 100.3, 2.0, '+y', 'manual fig 2-2'),
        ('USB BU301', 72.3, 95.3, 80.1, 101.2, 3.0, '+y', 'manual fig 2-2'),
        ('RJ45 X204', 82.1, 79.0, 99.3, 100.5, 13.5, '+y', 'manual fig 2-2'),
        ('JTAG X301 2x8', 55.5, 60.9, 76.9, 65.5, 8.5, 'top', 'manual fig 2-2'),
        ('DAP X302', 43.0, 57.0, 50.0, 66.0, 8.5, 'top', 'manual fig 2-2'),
        ('header X103 2x20', 1.1, 2.2, 6.1, 53.4, 8.5, 'top', 'manual fig 2-2'),
        ('header X102 2x20', 93.7, 1.3, 98.5, 52.5, 8.5, 'top', 'manual fig 2-2'),
        ('buzzer LS101', 26.6, 73.0, 41.5, 89.4, 9.0, None, 'manual fig 2-2, height assumed'),
        ('MCU U101', 21.0, 16.2, 38.7, 34.0, 2.5, None, 'manual fig 2-2'),
    ],
    under=[],
)

# --------------------------------------------------------------------------
# Espressif ESP32-S31-Function-CoreBoard-1 (v1.0). Everything from the
# published dimension DXF: outline and 58 x 48 hole rectangle from its DIMENSION
# entities, connector bodies from its silkscreen outlines.
#   https://dl.espressif.com/schematics/esp32-s31-function-coreboard-1-dimensions.dxf
# The WROOM-3 module hangs 6.00 mm past the left edge - the drawing dimensions
# it - so the antenna end needs nothing parked in front of it.
S31 = dict(
    size=(65.0, 55.0), hole_d=3.4, standoff=8.0,
    holes=[(3.5, 3.5), (61.5, 3.5), (3.5, 51.5), (61.5, 51.5)],
    parts=[
        ('module ESP32-S31-WROOM-3', -6.0, 9.2, 24.0, 31.2, 3.2, None, 'dimension DXF'),
        ('USB-C UART', 26.92, -0.8, 35.86, 7.38, 3.3, '-y', 'dimension DXF'),
        ('USB-C DBG', 39.22, -0.8, 48.16, 7.38, 3.3, '-y', 'dimension DXF'),
        ('RJ45 1GbE', 49.24, 20.05, 66.5, 36.55, 13.5, '+x', 'dimension DXF'),
        ('USB-A HS', 54.51, 12.12, 66.5, 17.84, 14.0, '+x', 'dimension DXF, stands on edge - height assumed'),
        ('magnetics', 39.0, 20.19, 46.1, 35.29, 6.0, None, 'dimension DXF'),
        ('header J2 2x20 (5V, G at the right end)', 6.34, 49.21, 58.66, 54.79, 8.5, 'top', 'dimension DXF'),
        ('speaker SPK', 0.0, 41.5, 3.4, 45.5, 4.0, '-x', 'dimension DXF, approximate'),
    ],
    under=[],
)

# --------------------------------------------------------------------------
# KA7-UNO CAN carrier. Connector spans from its fabrication set, drawn as
# blocks only. Connectors on THREE edges - CAN/LIN/POWER left, ETH0/T1S back,
# USB-C/RESET right; only the bottom edge is free. The ALINX AC7200 SoM plugs in UNDERNEATH (the board-to-board
# strips are on the solder side), with a 20 mm heatsink under that.
KA7 = dict(
    size=(70.0, 90.0), hole_d=3.4, standoff=35.0,
    holes=[(3.5, 3.5), (66.5, 3.5), (3.5, 86.5), (66.5, 86.5)],
    parts=[
        ('ETH0 RJ45', 47.10, 73.4, 63.40, 90.8, 13.5, '+y', 'fab set'),
        ('T1S0 CN1', 25.70, 80.0, 33.60, 90.5, 11.0, '+y', 'fab set, height assumed'),
        ('T1S1 CN2', 37.10, 80.0, 44.80, 90.5, 11.0, '+y', 'fab set, height assumed'),
        ('LIN0/1 J7', -0.5, 41.00, 8.7, 59.20, 12.0, '-x', 'fab set, height assumed'),
        ('CAN0/1 J3', -0.5, 21.70, 8.7, 39.90, 12.0, '-x', 'fab set, height assumed'),
        ('POWER J1', -0.5, 11.50, 10.6, 20.30, 12.0, '-x', 'fab set, height assumed'),
        ('header 2x5', 23.26, 23.93, 26.74, 35.45, 8.5, 'top', 'fab set'),
        # right edge: the silkscreen pin labels A1..B8 are a USB-C, its two
        # shell tabs at y 31.18 / 39.82; RESET sits over the outline notch
        ('USB-C (right edge)', 62.3, 31.0, 70.8, 40.0, 3.3, '+x', 'fab set silkscreen'),
        ('RESET button', 66.0, 11.3, 70.4, 16.3, 3.5, '+x', 'fab set, height assumed'),
    ],
    # (name, x0, y0, x1, y1, z_top_below_pcb, z_bottom_below_pcb)
    under=[('AC7200 SoM', 14.08, 1.48, 59.08, 56.48, 3.0, 7.22),
           ('heatsink 20 mm', 16.58, 8.98, 56.58, 48.98, 7.22, 27.22)],
)

# --------------------------------------------------------------------------
# Fault injection module, RJ45 build, 260910 (v2). From its KiCad PCB:
# Edge.Cuts outline, MountingHole footprints, F.CrtYd courtyards - blocks only.
# NOT the 260812 v1 board - 45.40 x 41.75 against 69.585 x 34.000.
FIM2 = dict(
    size=(45.40, 41.75), hole_d=2.9, standoff=20.0,
    holes=[(25.525, 3.60), (41.800, 4.00), (25.525, 38.06), (42.000, 38.46)],
    parts=[
        ('RJ45 J1', 0.08, -0.03, 17.78, 20.72, 13.5, '-x', 'KiCad courtyard'),
        ('RJ45 J2', 0.08, 20.94, 17.78, 41.68, 13.5, '-x', 'KiCad courtyard'),
        ('relay K1', 28.20, 13.70, 39.00, 29.20, 10.0, None, 'KiCad courtyard, height assumed'),
        ('socket J3 1x9', 39.47, 9.07, 43.01, 32.93, 8.5, 'top', 'KiCad courtyard'),
        ('socket J4 1x9', 24.23, 9.07, 27.77, 32.93, 8.5, 'top', 'KiCad courtyard'),
    ],
    under=[],
)

# --------------------------------------------------------------------------
# T1 connector gender. From its KiCad PCB (Edge.Cuts, MountingHole footprints,
# F.CrtYd), blocks only. J1/J2 are TE 9-2304372-9 (the MATEnet header the
# LAN9692 uses too), J3 a TE 2305987-1; all three face and overhang the
# bottom edge. Three MountingHole footprints plus J3's Ø2.5 peg in the
# fourth corner.
T1G = dict(
    size=(84.0, 28.4), hole_d=2.9, standoff=10.0,
    holes=[(3.375, 3.40), (80.826, 3.40), (3.049, 24.90), (80.500, 24.90)],
    parts=[
        ('MATEnet J2', 6.88, -2.25, 26.62, 20.85, 13.5, '-y', 'KiCad courtyard'),
        ('TE 2305987-1 J3', 27.07, -3.05, 54.52, 20.05, 12.0, '-y', 'KiCad courtyard, height assumed'),
        ('MATEnet J1', 57.58, -2.25, 77.32, 20.85, 13.5, '-y', 'KiCad courtyard'),
    ],
    under=[],
)

BOARDS = {'LAN9692': LAN9692, 'TC397': TC397, 'ESP32-S31': S31, 'KA7-UNO': KA7,
          'FIM-RJ45v2': FIM2, 'T1-Gender': T1G}
PCB_T = 1.6
