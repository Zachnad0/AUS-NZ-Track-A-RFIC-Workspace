#!/usr/bin/env python3
# extract_inductor.py -- openEMS L/Q/SRF extraction for vco_inductor_v2.
# UNTESTED pending openEMS install (bundled wheels are cp313/cp314; user has 3.12 --
# see queue). Geometry reproduced from team_src/magic/vco_inductor_v2.mag metal5 rects
# (scale 20 units/um) rather than re-parameterized, so it matches the drawn cell exactly.
# Method: lumped port PORT1<->PORT2, FDTD, then L=imag(Z11)/w, Q=imag/real, SRF at imag->0.
#
# Run (after install, on Windows, NOT in container):
#   py -3.13 extract_inductor.py
#
# gf180 metal5: thickness ~0.9um (top metal), sits ~ above substrate; use PDK stack values
# if available. Placeholder stack below -- refine from gf180 layer/thickness table before
# trusting Q/SRF (L is less sensitive to stack than Q).

import numpy as np
try:
    from CSXCAD import ContinuousStructure
    from openEMS import openEMS
    from openEMS.physical_constants import C0
except ImportError as e:
    raise SystemExit("openEMS/CSXCAD not importable -- install the wheels first (see queue). %s" % e)

U = 0.05  # um per .mag unit (20 units/um -> 0.05 um/unit)
MET5_Z0, MET5_TH = 10.0, 0.9   # um: metal5 bottom height, thickness (PLACEHOLDER -- set from gf180 stack)

# metal5 rects from vco_inductor_v2.mag (x1,y1,x2,y2 in .mag units) -- both halves
MET5 = [
 (-2240,-160,-2080,1040),(-2040,840,-920,1000),(-2040,40,-1880,840),(-1840,640,-1120,800),
 (-1840,240,-1680,640),(-1840,230,-1320,240),(-1840,90,-1470,230),(-1330,90,-1320,230),
 (-1840,80,-1320,90),(-1280,40,-1120,640),(-2040,-120,-1120,40),(-1080,-160,-920,840),
 (-2240,-320,-920,-160),(-880,-480,-720,1040),(-120,-480,40,1040),(80,840,1200,1000),
 (80,-160,240,840),(280,640,1000,800),(280,40,440,640),(840,240,1000,640),
 (480,230,1000,240),(480,90,490,230),(630,90,1000,230),(480,80,1000,90),
 (1040,40,1200,840),(280,-120,1200,40),(1240,-160,1400,1040),(80,-320,1400,-160),
]
PORT1 = (-800,-480); PORT2 = (-40,-480)   # rlabels, .mag units

FSTART, FSTOP = 0.1e9, 20e9

FDTD = openEMS(NrTS=60000, EndCriteria=1e-4)
FDTD.SetGaussExcite(0.5*(FSTART+FSTOP), 0.5*(FSTOP-FSTART))
FDTD.SetBoundaryCond(['MUR']*6)

CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
met = CSX.AddMetal('metal5')
for (x1,y1,x2,y2) in MET5:
    met.AddBox([x1*U, y1*U, MET5_Z0], [x2*U, y2*U, MET5_Z0+MET5_TH])

# lumped port across the two terminals (series L seen as Z11 of a 1-port on the diff pair)
p1 = [PORT1[0]*U, PORT1[1]*U, MET5_Z0]; p2 = [PORT2[0]*U, PORT2[1]*U, MET5_Z0+MET5_TH]
port = FDTD.AddLumpedPort(1, 50, p1, p2, 'z', excite=1)

# mesh: fixed lines on all metal edges + thirds rule; refine near the port
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1e-6)
xs=set(); ys=set()
for (x1,y1,x2,y2) in MET5:
    xs.update([x1*U,x2*U]); ys.update([y1*U,y2*U])
pad=200
mesh.AddLine('x', sorted(xs)+[min(xs)-pad, max(xs)+pad])
mesh.AddLine('y', sorted(ys)+[min(ys)-pad, max(ys)+pad])
mesh.AddLine('z', [MET5_Z0-50, MET5_Z0, MET5_Z0+MET5_TH, MET5_Z0+MET5_TH+50, -100, 200])
mesh.SmoothMeshLines('all', 4.0)

import tempfile, os
simdir = os.path.join(tempfile.gettempdir(), 'ind_em')
FDTD.Run(simdir, cleanup=True)

f = np.linspace(FSTART, FSTOP, 401)
port.CalcPort(simdir, f)
Z = port.uf_tot / port.if_tot
w = 2*np.pi*f
L = np.imag(Z)/w
Q = np.imag(Z)/np.real(Z)
# SRF = first f where imag(Z) crosses zero (L->inf then negative)
srf = f[np.where(np.diff(np.sign(np.imag(Z))))[0][0]] if np.any(np.diff(np.sign(np.imag(Z)))) else None
i1g = np.argmin(np.abs(f-1e9))
print("L @1GHz   = %.3f nH   (pi-model 1.2 nH)" % (L[i1g]*1e9))
print("Q @1GHz   = %.1f" % Q[i1g])
print("SRF       = %s GHz" % (("%.1f"%(srf/1e9)) if srf else "not in band"))
np.savetxt(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ind_LQ.dat'),
           np.column_stack([f, L, Q]), header='f  L(H)  Q')
