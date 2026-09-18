"""Measure f0, differential swing, startup time to 90 %, supply current and amplitude drift
from a wrdata dump of the VCO bench."""
import sys
import numpy as np

path = sys.argv[1]
t0w = float(sys.argv[2]) if len(sys.argv) > 2 else 30e-9
t1w = float(sys.argv[3]) if len(sys.argv) > 3 else 40e-9

raw = np.loadtxt(path)
# ngspice wrdata emits a time column before every variable
t = raw[:, 0]
net1, net2 = raw[:, 1], raw[:, 3]
outp, outn = raw[:, 5], raw[:, 7]
iv1, iiss = raw[:, 9], raw[:, 11]
diff = net1 - net2

print("rows %d   t %.3f .. %.3f ns" % (len(t), t[0] * 1e9, t[-1] * 1e9))


def envelope(tt, y, win):
    """peak-to-peak in a sliding window of `win` seconds"""
    out = []
    i = 0
    while i < len(tt):
        j = i
        while j < len(tt) and tt[j] < tt[i] + win:
            j += 1
        if j > i + 2:
            out.append((0.5 * (tt[i] + tt[j - 1]), y[i:j].max() - y[i:j].min()))
        i = j
    return np.array(out)


def f_zero_cross(tt, y):
    """frequency from mean spacing of rising zero crossings of a mean-removed signal"""
    z = y - y.mean()
    idx = np.where((z[:-1] < 0) & (z[1:] >= 0))[0]
    if len(idx) < 3:
        return float("nan"), 0
    xs = tt[idx] + (tt[idx + 1] - tt[idx]) * (-z[idx]) / (z[idx + 1] - z[idx])
    per = np.diff(xs)
    return 1.0 / per.mean(), len(xs)


m = (t >= t0w) & (t <= t1w)
f0, nx = f_zero_cross(t[m], diff[m])
pp = diff[m].max() - diff[m].min()
print()
print("  window %.1f-%.1f ns, %d rows, %d rising crossings" % (t0w * 1e9, t1w * 1e9, m.sum(), nx))
print("  f0 (core net1-net2)          : %.4f GHz" % (f0 / 1e9))
print("  differential swing           : %.4f Vpp" % pp)
print("  supply current  mean i(v1)   : %.4f mA" % (abs(iv1[m].mean()) * 1e3))
print("  tail current    mean i(viss) : %.4f mA" % (abs(iiss[m].mean()) * 1e3))

# amplitude drift across the window: first half vs second half
mid = 0.5 * (t0w + t1w)
a1 = diff[(t >= t0w) & (t < mid)]
a2 = diff[(t >= mid) & (t <= t1w)]
pp1, pp2 = a1.max() - a1.min(), a2.max() - a2.min()
drift = abs(pp2 - pp1) / (0.5 * (pp1 + pp2)) * 100
print("  amplitude %.1f-%.1f / %.1f-%.1f ns : %.4f / %.4f Vpp  -> drift %.3f %%"
      % (t0w * 1e9, mid * 1e9, mid * 1e9, t1w * 1e9, pp1, pp2, drift))
print("  settled (<1 %%)               : %s" % ("YES" if drift < 1.0 else "NO"))

# startup: first time the sliding-window envelope reaches 90 % of the settled p-p
env = envelope(t, diff, 0.4e-9)
target = 0.9 * pp
hit = [e for e in env if e[1] >= target]
if hit:
    print("  startup to 90 %% of %.3f Vpp  : %.3f ns" % (pp, hit[0][0] * 1e9))
else:
    print("  startup to 90 %%              : NOT REACHED in the run")
print()
print("  envelope trace (p-p per 2 ns):")
env2 = envelope(t, diff, 2e-9)
print("   " + "  ".join("%.0fns:%.2f" % (e[0] * 1e9, e[1]) for e in env2))
