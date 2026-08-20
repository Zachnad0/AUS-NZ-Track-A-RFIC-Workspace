#!/usr/bin/env python3
# klayout_signoff.py <CELL> -- run the KLayout variant-D signoff DRC on gds/<CELL>.gds and
# apply a PER-CELL accepted-rules waiver from team_src/magic/<CELL>.waivers (one rule name per
# line; blank/`#` lines ignored). Violations of a waived rule are reported as WAIVED with their
# count; ANY other violated rule fails the gate. No rule is silenced globally -- only the exact
# names in that cell's .waivers file are accepted, and only for that cell.
#
# Exit 0 iff every violated rule is waived (or there are none); exit 1 otherwise.
import sys, os, subprocess, xml.etree.ElementTree as ET
from collections import Counter

REPO = "/foss/designs/AUS-NZ-integration"
RUN_DRC = REPO + "/gf180mcu/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py"

def main():
    if len(sys.argv) != 2:
        print("usage: klayout_signoff.py <CELL>", file=sys.stderr); return 2
    cell = sys.argv[1]
    gds = "%s/gds/%s.gds" % (REPO, cell)
    if not os.path.isfile(gds):
        print("FATAL: no layout %s" % gds, file=sys.stderr); return 3
    wfile = "%s/team_src/magic/%s.waivers" % (REPO, cell)
    waived = set()
    if os.path.isfile(wfile):
        for ln in open(wfile):
            ln = ln.split("#", 1)[0].strip()
            if ln:
                waived.add(ln)
    work = "/tmp/sign_%s" % cell
    subprocess.run(["rm", "-rf", work]); os.makedirs(work, exist_ok=True)
    subprocess.run(["python3", RUN_DRC, "--path=" + gds, "--variant=D",
                    "--topcell=" + cell, "--run_dir=" + work, "--run_mode=flat"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lyrdb = "%s/%s_main.lyrdb" % (work, cell)
    if not os.path.isfile(lyrdb):
        print("FATAL: DRC produced no report (%s)" % lyrdb, file=sys.stderr); return 3
    cat = Counter()
    for it in ET.parse(lyrdb).getroot().iter("item"):
        cat[it.findtext("category", "").strip("'\"")] += 1

    print("== KLayout signoff (variant D): %s ==" % cell)
    print("   waivers file: %s  [%s]" % (wfile if os.path.isfile(wfile) else "(none)",
                                         " ".join(sorted(waived)) or "-"))
    if not cat:
        print("   DRC CLEAN (0 violations)"); print("RESULT: PASS"); return 0
    hard = 0
    for rule in sorted(cat):
        n = cat[rule]
        if rule in waived:
            print("   WAIVED    %-10s x%d" % (rule, n))
        else:
            print("   VIOLATION %-10s x%d" % (rule, n)); hard += cat[rule]
    if hard:
        print("RESULT: FAIL (%d non-waived violations)" % hard); return 1
    print("RESULT: PASS (all %d violations waived)" % sum(cat.values())); return 0

if __name__ == "__main__":
    sys.exit(main())
