#!/usr/bin/env python3
# chip_conn.py -- dump chip_top's block-instance port->net mapping from the extracted netlist
# (verify_work/chip_top.lvs.spice), so routing rungs can be diffed for silent shorts/merges.
# Usage: chip_conn.py            -> print current mapping
#        chip_conn.py save NAME  -> also save a snapshot to /tmp/chipconn_NAME.txt
#        chip_conn.py diff NAME  -> print current AND unified-diff vs snapshot NAME
import sys, os, re

LVS = "/foss/designs/AUS-NZ-integration/team_src/magic/verify_work/chip_top.lvs.spice"
BLOCKS = ["PFD_lib", "CP_v1", "ibias_gen_v1", "DIV2_QUAD_v1", "vco_v1"]
PORTS = {}  # filled from the extracted .subckt lines (true port order)

def read_map():
    if not os.path.isfile(LVS):
        return {}
    txt = open(LVS).read()
    for b in BLOCKS:
        m = re.search(r"^\.subckt %s\s+(.*)$" % re.escape(b), txt, re.M)
        if m:
            PORTS[b] = m.group(1).split()
    # grab chip_top subckt body
    m = re.search(r"^\.subckt chip_top.*?^\.ends", txt, re.S | re.M)
    body = m.group(0) if m else txt
    # join continuation lines (xschem/magic wrap with leading '+')
    body = re.sub(r"\n\+", " ", body)
    out = {}
    for line in body.splitlines():
        line = line.strip()
        m = re.match(r"^X(\w+?)_0\s+(.*)", line)
        if not m:
            continue
        inst = m.group(1)
        if inst not in PORTS:
            continue
        toks = m.group(2).split()
        # last token is the subckt name; the ones before are net connections
        nets = toks[:-1]
        names = PORTS[inst]
        if len(nets) >= len(names):
            out[inst] = dict(zip(names, nets[:len(names)]))
    return out

def fmt(mp):
    lines = []
    for inst in sorted(mp):
        for port in PORTS[inst]:
            lines.append("%-14s.%-7s = %s" % (inst, port, mp[inst].get(port, "?")))
    return "\n".join(lines)

def main():
    mp = read_map()
    cur = fmt(mp)
    print(cur if cur else "(no extraction found -- run verify_cp.sh chip_top first)")
    if len(sys.argv) >= 3 and sys.argv[1] in ("save", "diff"):
        snap = "/tmp/chipconn_%s.txt" % sys.argv[2]
        if sys.argv[1] == "save":
            open(snap, "w").write(cur + "\n")
            print("\n[saved snapshot %s]" % snap)
        else:
            if not os.path.isfile(snap):
                print("\n[no snapshot %s]" % snap); return
            import difflib
            old = open(snap).read().splitlines()
            d = list(difflib.unified_diff(old, cur.splitlines(), "prev", "now", lineterm=""))
            print("\n==== DIFF vs %s ====" % sys.argv[2])
            print("\n".join(d) if d else "(no change)")

if __name__ == "__main__":
    main()
