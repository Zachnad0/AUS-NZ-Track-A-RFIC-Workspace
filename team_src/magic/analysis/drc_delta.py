#!/usr/bin/env python3
# drc_delta.py <baseline.dump> <candidate.dump> [--shift DX_IU DY_IU]
#
# Compare two drc_boxset.tcl dumps as MULTISETS of violation boxes.
#
# WHY: magic's `drc list count total` is frame-dependent -- seating chip_top inside the
# A01_BH DIEAREA (a pure +200/+200 translation) moved the total 84 -> 106 with the violation
# set bit-identical (252 boxes both sides, 0 extra, 0 missing). A phase-8 gate that compares
# totals would have read that as 22 new violations; a gate that compares box sets reads it
# correctly as zero change. Totals are for reporting; the box set is the gate.
#
# --shift adds (DX_IU, DY_IU) to every BASELINE box before comparing, so a dump taken in the
# core frame can be compared against one taken in the die frame. magic internal units here are
# 1 iu = 1 GDS dbu = 0.005 um, so the +200/+200 seat is --shift 40000 40000.
#
# Exit 0 iff the candidate has no boxes the baseline lacks. Boxes the baseline has and the
# candidate lacks are reported too (violations that disappeared are also a change worth
# seeing) but do not by themselves fail the gate.
#
# COMPLETENESS (exit 3). Since 2026-08-25 drc_boxset.tcl emits `SELFCHECK OK|FAIL`, asserting
# that it walked every {rule}{boxes} pair `drc listall why` returned. A dump reporting FAIL is
# REFUSED here rather than compared, because a short dump is a FALSE PASS: drop boxes from the
# candidate and `added` is empty, so the gate reads "no violations added" and returns 0. That
# is the worst failure mode this tool has. A dump with no SELFCHECK line predates the format;
# it is compared, with its completeness flagged as unverified.
#
# PROVENANCE. A .drcbase is only meaningful against the GDS it was dumped from. Dumps now carry
# `GDSBLOB` (git blob sha of the GDS) and `SRCCOMMIT` (repo HEAD), and a mismatch between the
# two sides is reported LOUDLY. This existed as a silent trap: the 2026-08-22 baseline was
# dumped before five phase-8 routing commits, and the only symptom of comparing across them was
# a TOTAL of 106 vs 108 that nobody reads. The box set was identical throughout -- the gate was
# right -- but nothing said the layouts differed.
import sys
from collections import Counter

DBU = 0.005  # um per internal unit


def load(path, shift=(0, 0)):
    boxes = Counter()
    total = None
    rules = []
    # Provenance + completeness header, emitted by drc_boxset.tcl since 2026-08-25.
    # Dumps older than that carry none of these; that is reported, not treated as an error.
    meta = {"GDSF": None, "GDSBLOB": None, "SRCCOMMIT": None, "SELFCHECK": None}
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            if p[0] == "TOTAL":
                total = int(p[1])
            elif p[0] in ("GDSF", "GDSBLOB", "SRCCOMMIT"):
                meta[p[0]] = p[1] if len(p) > 1 else None
            elif p[0] == "SELFCHECK":
                meta["SELFCHECK"] = " ".join(p[1:])
            elif p[0] == "RULE":
                rules.append((int(p[1]), " ".join(p[2:])))
            elif p[0] == "B" and len(p) == 5:
                v = [int(x) for x in p[1:]]
                boxes[(v[0] + shift[0], v[1] + shift[1], v[2] + shift[0], v[3] + shift[1])] += 1
    return total, boxes, rules, meta


def um(b):
    return "(%.3f,%.3f)-(%.3f,%.3f)" % (b[0] * DBU, b[1] * DBU, b[2] * DBU, b[3] * DBU)


def main(argv):
    if len(argv) < 3:
        print("usage: drc_delta.py <baseline.dump> <candidate.dump> [--shift DX_IU DY_IU]",
              file=sys.stderr)
        return 2
    shift = (0, 0)
    if "--shift" in argv:
        i = argv.index("--shift")
        shift = (int(argv[i + 1]), int(argv[i + 2]))

    bt, bb, br, bm = load(argv[1], shift)
    ct, cb, cr, cm = load(argv[2])

    # A truncated dump reads downstream as "no violations added" -- a false PASS, and the
    # worst failure mode this tool has. Refuse to compare one at all.
    for lbl, path, m in (("baseline", argv[1], bm), ("candidate", argv[2], cm)):
        sc = m["SELFCHECK"]
        if sc is not None and not sc.startswith("OK"):
            print("FATAL: %s dump %s reports SELFCHECK %s" % (lbl, path, sc), file=sys.stderr)
            print("       The dump is incomplete. Re-run drc_boxset.tcl; do not gate on this.",
                  file=sys.stderr)
            return 3

    print("baseline : %s  TOTAL=%s  boxes=%d  (shift %+d,%+d iu applied)"
          % (argv[1], bt, sum(bb.values()), shift[0], shift[1]))
    print("candidate: %s  TOTAL=%s  boxes=%d" % (argv[2], ct, sum(cb.values())))

    # PROVENANCE. A .drcbase is only meaningful against the GDS it was dumped from. The
    # 2026-08-22 baseline was silently compared against five commits' worth of newer layout;
    # the only symptom was a TOTAL nobody reads. Say it out loud instead.
    for lbl, m in (("baseline ", bm), ("candidate", cm)):
        if m["GDSBLOB"] or m["SRCCOMMIT"]:
            print("   %s gds blob %s  from commit %s"
                  % (lbl, (m["GDSBLOB"] or "unknown")[:12], (m["SRCCOMMIT"] or "unknown")[:12]))
        else:
            print("   %s no provenance header (dump predates 2026-08-25 format)" % lbl)
    if bm["GDSBLOB"] and cm["GDSBLOB"] and bm["GDSBLOB"] != cm["GDSBLOB"]:
        print()
        print("PROVENANCE MISMATCH: the two dumps are of DIFFERENT layouts.")
        print("   baseline  gds %s" % bm["GDSBLOB"])
        print("   candidate gds %s" % cm["GDSBLOB"])
        print("   A zero delta below still means no violation box was ADDED, which is the")
        print("   gate. But TOTAL and per-cell counts are not comparable across layouts,")
        print("   and if you expected the same GDS on both sides, something moved.")
    if any(m["SELFCHECK"] is None for m in (bm, cm)):
        print("   NOTE: a dump without SELFCHECK has unverified completeness (old format).")
    for n, r in br:
        print("   baseline  rule x%-4d %s" % (n, r))
    for n, r in cr:
        print("   candidate rule x%-4d %s" % (n, r))

    added = cb - bb
    gone = bb - cb
    print()
    if bt != ct:
        print("NOTE: totals differ (%s -> %s). That alone means nothing -- magic's per-cell"
              % (bt, ct))
        print("      attribution is frame-dependent. The box set below is the real answer.")
    print("ADDED   (in candidate, not in baseline): %d" % sum(added.values()))
    for b, n in sorted(added.items())[:40]:
        print("   + x%d %s um %s" % (n, b, um(b)))
    if sum(added.values()) > 40:
        print("   ... %d more" % (sum(added.values()) - 40))
    print("REMOVED (in baseline, not in candidate): %d" % sum(gone.values()))
    for b, n in sorted(gone.items())[:40]:
        print("   - x%d %s um %s" % (n, b, um(b)))
    if sum(gone.values()) > 40:
        print("   ... %d more" % (sum(gone.values()) - 40))

    print()
    if not added:
        print("RESULT: PASS -- no violation box in the candidate that the baseline lacks.")
        return 0
    print("RESULT: FAIL -- %d added violation box(es)." % sum(added.values()))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
