#!/usr/bin/env python3
# ind_em.py -- openEMS FDTD extraction of vco_inductor_v2 (6.2).
# Parses team_src/magic/vco_inductor_v2/vco_inductor_v2.mag (20 units/um), builds the
# gf180mcuD metal4/via4/metal5/rm5 stack at real z-heights, feeds a differential lumped
# port ACROSS THE 30um GAP between the two metal5 leads (no ground plane => Z11 = jwL + R
# of the whole coil), sweeps to 20 GHz, reports L / Q / SRF vs the analytical 1.2 nH.
#
# STATUS (2026-08-14): geometry parse + gf180 stackup + gap port + mesh all BUILD and the
# FDTD engine RUNS (verified: 32k cells, dt 9.6e-16 s, ~3-6 MCells/s). SOLVE DEFERRED under
# rule 4: the low-freq Gaussian pulse needs ~297k timesteps (pulse 2.9e-10 s / dt), and dt
# is capped at 9.6e-16 s by the 0.55um metal4 thickness (a thin 3D z-cell). Full 3D solve
# ~= 50 min -> over the 15 min/launch ceiling.
#   FIX (resume point): model metal4/metal5 as openEMS CONDUCTING SHEETS (thin, zero
#   z-extent) so the z-mesh coarsens to ~1.5um -> dt ~3e-15 s -> ~100k excite steps ->
#   ~11 min solve. Re-place the gap port on the metal5 sheet plane. Then this script's
#   post-processing (Z11 -> L/Q/SRF) runs unchanged.
#
# Runtime guard: env NUMTS caps timesteps for probing; BUILD_ONLY writes CSX without running.
import os, sys, re, numpy as np
from CSXCAD import CSXCAD
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0, MUE0

UNIT   = 0.05e-6          # mag internal unit = 0.05 um  (20 units/um)
MAG    = os.environ.get('MAGFILE',
         '/foss/designs/AUS-NZ-integration/team_src/magic/vco_inductor_v2/vco_inductor_v2.mag')
OUTDIR = os.environ.get('OUTDIR', '/tmp/ind_em')
NUMTS  = int(os.environ.get('NUMTS', '400'))
FMAX   = 20e9
SIGMA_AL = 3.5e7          # gf180 Al metallization
EPS_ILD  = 4.0            # SiO2 ILD

# gf180mcuD z-stack (um -> m), from libs.tech/magic/gf180mcuD.tech "height" lines
Z = {  # layer: (z_bottom_um, z_top_um)
    'metal4': (4.68, 5.23),
    'via4':   (5.23, 5.83),
    'metal5': (5.83, 6.8325),
    'rm5':    (5.83, 6.8325),   # top redistribution -- modeled coincident with metal5
}

def parse_mag(path):
    layers = {}
    cur = None
    ports = {}
    for ln in open(path):
        m = re.match(r'<<\s*(\S+)\s*>>', ln)
        if m:
            cur = m.group(1); layers.setdefault(cur, [])
            continue
        r = re.match(r'rect\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', ln)
        if r and cur is not None:
            layers[cur].append(tuple(int(v) for v in r.groups()))
        p = re.match(r'rlabel\s+\S+\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+\d+\s+(\S+)', ln)
        if p:
            ports[p.group(5)] = (int(p.group(1)), int(p.group(2)))
    return layers, ports

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    layers, ports = parse_mag(MAG)
    print('layers:', {k: len(v) for k, v in layers.items()})
    print('ports :', ports)

    FDTD = openEMS(NrTS=NUMTS, EndCriteria=1e-4)
    FDTD.SetGaussExcite(FMAX/2, FMAX/2)
    FDTD.SetBoundaryCond(['MUR']*6)
    CSX = CSXCAD.ContinuousStructure()
    FDTD.SetCSX(CSX)

    al = CSX.AddMaterial('al_mat', kappa=SIGMA_AL)   # lossy aluminium (finite conductivity)

    allx, ally = [], []
    def add_rects(rects, zb, zt, mat):
        nonlocal allx, ally
        for (x1, y1, x2, y2) in rects:
            X1, X2 = sorted((x1*UNIT, x2*UNIT)); Y1, Y2 = sorted((y1*UNIT, y2*UNIT))
            mat.AddBox([X1, Y1, zb*1e-6], [X2, Y2, zt*1e-6])
            allx += [X1, X2]; ally += [Y1, Y2]

    for lay in ('metal4', 'via4', 'metal5', 'rm5'):
        if lay in layers:
            add_rects(layers[lay], Z[lay][0], Z[lay][1], al)

    xmin, xmax = min(allx), max(allx); ymin, ymax = min(ally), max(ally)
    z5b, z5t = Z['metal5'][0]*1e-6, Z['metal5'][1]*1e-6

    # ---- lumped port in the 30um gap between the two metal5 leads (differential,
    #      no ground plane): excites across PORT1-lead (right edge -720u) to
    #      PORT2-lead (left edge -120u). Z11 = jwL + R of the whole coil. ----
    pstart = [-720*UNIT, -480*UNIT, z5b]
    pstop  = [-120*UNIT, -320*UNIT, z5t]
    port = FDTD.AddLumpedPort(1, 50, pstart, pstop, 'x', 1.0, priority=100)

    # ---- mesh. DECIMATE in-plane edges to a >=MINCELL spacing: the layout has
    #      0.5um underpass slivers that would force a tiny FDTD timestep (CFL) and a
    #      multi-hour low-freq solve. Sub-um features are cosmetic for total L. ----
    MINCELL = 1.5e-6
    def decimate(vals, keep=()):
        vals = sorted(set(np.round(vals, 10)))
        out = [vals[0]]
        for v in vals[1:]:
            if v in keep or (v - out[-1]) >= MINCELL: out.append(v)
        return np.array(out)
    mesh = CSX.GetGrid(); mesh.SetDeltaUnit(1.0)
    padxy = 120e-6; padz = 120e-6
    keepx = (-720*UNIT, -120*UNIT); keepy = (-480*UNIT, -320*UNIT)
    xl = decimate(list(allx) + [xmin-padxy, xmax+padxy] + list(keepx), keepx)
    yl = decimate(list(ally) + [ymin-padxy, ymax+padxy] + list(keepy), keepy)
    # z: metal boundaries only (>=0.55um apart) + air pads; no sub-um z cells
    zl = np.round([4.68e-6-padz, 4.68e-6, 5.23e-6, 5.83e-6, 6.8325e-6, 6.8325e-6+padz], 12)
    mesh.AddLine('x', xl); mesh.AddLine('y', yl); mesh.AddLine('z', zl)
    mesh.SmoothMeshLines('x', 20e-6, 1.4)
    mesh.SmoothMeshLines('y', 20e-6, 1.4)
    mesh.SmoothMeshLines('z', 25e-6, 1.5)

    nx = len(mesh.GetLines('x')); ny = len(mesh.GetLines('y')); nz = len(mesh.GetLines('z'))
    print('MESH cells: %d x %d x %d = %.3f M' % (nx, ny, nz, nx*ny*nz/1e6))

    CSX.Write2XML(os.path.join(OUTDIR, 'ind_em.xml'))
    if os.environ.get('BUILD_ONLY'):
        print('BUILD_ONLY set -- CSX written, not running.'); return

    FDTD.Run(OUTDIR, verbose=3, cleanup=True, numThreads=int(os.environ.get('NTHREADS', '4')))

    f = np.linspace(1e8, FMAX, 601)
    port.CalcPort(OUTDIR, f)
    Zin = port.uf_tot / port.if_tot
    L = np.imag(Zin) / (2*np.pi*f)
    Q = np.imag(Zin) / np.real(Zin)
    # SRF = first freq where Im(Zin) crosses zero going negative
    srf = None
    im = np.imag(Zin)
    for i in range(1, len(f)):
        if im[i-1] > 0 and im[i] <= 0:
            srf = f[i-1] + (f[i]-f[i-1]) * im[i-1]/(im[i-1]-im[i]); break
    i1 = np.argmin(np.abs(f-1e9)); i24 = np.argmin(np.abs(f-2.4e9)); i5 = np.argmin(np.abs(f-5e9))
    print('=== RESULT ===')
    print('L @1GHz  = %.3f nH   Q=%.1f' % (L[i1]*1e9, Q[i1]))
    print('L @2.4GHz= %.3f nH   Q=%.1f' % (L[i24]*1e9, Q[i24]))
    print('L @5GHz  = %.3f nH   Q=%.1f' % (L[i5]*1e9, Q[i5]))
    print('SRF      = %s' % ('%.2f GHz' % (srf/1e9) if srf else '> %g GHz' % (FMAX/1e9)))
    print('pi-model = 1.2 nH  (target)')
    np.savetxt(os.path.join(OUTDIR, 'ZLQ.txt'),
               np.c_[f, np.real(Zin), np.imag(Zin), L*1e9, Q], header='f Re Im L_nH Q')

if __name__ == '__main__':
    main()
