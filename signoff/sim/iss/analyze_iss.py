"""Differential swing and f0 over 190-200 ns from a mk_vco_iss.py .dat dump."""
import sys
for f in sys.argv[1:]:
    t, d = [], []
    for line in open(f):
        p = line.split()
        if len(p) < 6 or float(p[0]) < 190e-9:
            continue
        t.append(float(p[0])); d.append(float(p[1]) - float(p[3]))
    pp = max(d) - min(d)
    z = [t[i-1] + (t[i]-t[i-1]) * (-d[i-1]) / (d[i]-d[i-1]) for i in range(1, len(d)) if d[i-1] < 0 <= d[i]]
    f0 = (len(z)-1) / (z[-1]-z[0]) / 1e9 if len(z) > 2 and pp > 0.05 else 0.0
    print(f"{f}: diff {pp:.3f} Vpp  f0 {f0:.3f} GHz")
