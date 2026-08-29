#!/usr/bin/env python3
# ref_audit.py -- every cross-reference in the docs must resolve. Run from the repo root:
#
#     python3 team_src/magic/analysis/ref_audit.py .
#
# Exit 0 iff nothing dangles. Two independent classes, both gating:
#
#   SECTION refs -- "§8.10", "§1a-1d". Resolved against the headings of the file the ref
#     appears in, falling back to a .md named on the same line. THIS IS THE CLASS THAT MUST
#     STAY REPRODUCIBLE: a doc pointing at a section number that does not exist is a silent
#     lie, and we have shipped three -- phase8-padframe-plan's §1a and §1b (those subsections
#     were headed "### BV" / "### BH"), and scope.md's §3.1, which named a subsection the
#     frequency-plan rewrite had already removed.
#
#   PATH refs -- a backticked repo-relative path. CANNOT be adjudicated by existence alone:
#     the docs legitimately name organizer-side files, Bailey's own scripts, and one file we
#     deliberately cite as RETIRED. Those live in ALLOWLIST below, each with a reason, so a
#     clean run means something. An unresolved path NOT on the allowlist fails; an allowlist
#     entry that has become resolvable or unreferenced is ALSO reported, so the list cannot
#     rot silently.
#
# WHY EXISTENCE ALONE IS NOT ENOUGH -- the false positives this had to learn:
#   - a backticked name is often a BASENAME whose directory was named in nearby prose;
#   - "`vco_v1.sch/.sym`" is prose for a PAIR of files, not one path;
#   - a path written relative to the PDK root resolves under the vendored gf180mcu/ copy.
# All three are handled below. Do NOT "fix" a doc to satisfy this tool without working out
# which case it is -- see the ib_inv1.tcl entry for how that is supposed to go.
import io, os, re, sys, glob

# path -> why it cannot resolve in this repo. Keep each reason specific enough that a future
# reader can tell genuine rot from an intentional outside reference.
ALLOWLIST = {
    "Workshop_CASS/padring/workshop_padring.cfg":
        "organizers' Workshop_CASS repo, not vendored here",
    "workshop_padring.cfg":
        "same file, basename form (CREDITS.md / padring-README.md / workshop-slot-spec.md)",
    "scripts/gds.analog.spice.tcl":
        "Bailey's LVS flow, described not shipped; ours is team_src/magic/bailey_*.tcl",
    "abstract.tcl":
        "Bailey's PASS 1 script; ours is team_src/magic/bailey_pass1_abstract.tcl",
    "extract.tcl":
        "Bailey's PASS 2 script; ours is team_src/magic/bailey_pass2_extract.tcl",
    "capa.sym":
        "xschem stock symbol library, outside the project",
    "ib_inv1.tcl":
        "DELIBERATE: cited as retired history. Added e80f175, DELETED the same day in "
        "38f317d when make_inv absorbed it. docs/div2-layout-plan.md says so explicitly.",
    "extra_be_checks/tech/gf180mcuD/lvs_config.user_project_wrapper.json":
        "organizer-supplied, resolves under $LVS_ROOT at their end",
    "extra_be_checks/tech/gf180mcuD/lvs_config.base.json":
        "organizer-supplied, resolves under $LVS_ROOT at their end",
    "tech/gf180mcuD/lvs_config.base.json":
        "same file written $LVS_ROOT-relative",
    "user_project_wrapper.json":
        "organizer template name, not a file we carry",
    "_iqtaps.py":
        "throwaway analysis script, never committed by design",
    "scratchpad/issue143_aug14_review_draft.md":
        "deliberately uncommitted scratch",
    "A01.def":
        "the organizers' delivered tarball, not a repo path",
    "io_secondary_3p3.sch":
        "lives in sscs-chipathon-2026, not vendored here",
}

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
HEAD = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*[a-z]?)\.?\s")
SEC  = re.compile(r"[§]\s?(\d+(?:\.\d+)*[a-z]?)(?:\s*[–—-]\s*(\d+(?:\.\d+)*[a-z]?))?")
DOCM = re.compile(r"(?:docs/)?([A-Za-z0-9_.-]+\.md)")
PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:py|tcl|sh|md|json|yaml|yml|spice|sch|"
                  r"sym|mag|gds|def|cfg|drc|lvs|tech|waivers|drcbase|abstract))`")


def split(n):
    m = re.match(r"^(\d+(?:\.\d+)*)([a-z]?)$", n)
    return (m.group(1), m.group(2)) if m else (n, "")


def expand(a, b):
    """A ranged ref must have EVERY endpoint resolve. "supersedes §1a-1d" dangled on 1a and
    1b while 1c and 1d were fine; only expanding the range makes that visible."""
    if b is None:
        return [a]
    pa, la = split(a); pb, lb = split(b)
    if pa == pb and la and lb and la <= lb:
        return [pa + chr(c) for c in range(ord(la), ord(lb) + 1)]
    if not la and not lb and "." not in pa and "." not in pb:
        try:
            if int(pa) <= int(pb):
                return [str(i) for i in range(int(pa), int(pb) + 1)]
        except ValueError:
            pass
    if pa == pb and not la and not lb:
        return [a]
    return [a, b]


ALLNAMES, ALLREL = set(), set()
for dp, dns, fns in os.walk(ROOT):
    dns[:] = [d for d in dns if d not in (".git", "node_modules")]
    ALLNAMES.update(fns)
    ALLREL.update(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/") for f in fns)

files = sorted(glob.glob(os.path.join(ROOT, "docs", "*.md"))
               + glob.glob(os.path.join(ROOT, "*.md")))
heads = {}
for f in files:
    hs = set()
    for line in io.open(f, encoding="utf-8", errors="replace"):
        m = HEAD.match(line)
        if m:
            hs.add(m.group(1))
    heads[os.path.basename(f)] = hs

bad_sec, bad_path, nsec, npath, used = [], [], 0, 0, set()
for f in files:
    base = os.path.basename(f)
    for i, line in enumerate(io.open(f, encoding="utf-8", errors="replace"), 1):
        if line.lstrip().startswith("#"):
            continue                              # a heading is not a reference
        # OWN FILE FIRST. A section ref almost always points at its own doc; a filename
        # elsewhere on the line is only a fallback target. Retargeting eagerly turned three
        # good refs in phase8-padframe-plan.md into false positives purely because the line
        # happened to name analysis/README.md.
        dm = DOCM.search(line)
        alt = dm.group(1) if dm and dm.group(1) in heads else None
        for m in SEC.finditer(line):
            for n in expand(m.group(1), m.group(2)):
                nsec += 1
                if n in heads.get(base, ()):
                    continue
                if alt and n in heads.get(alt, ()):
                    continue
                bad_sec.append((base, i, n, base if not alt else base + " or " + alt))
        for m in PATH.finditer(line):
            rel = m.group(1); npath += 1
            if os.path.exists(os.path.join(ROOT, rel)):
                continue
            if os.path.basename(rel) in ALLNAMES:
                continue
            if rel.endswith(".sch/.sym") and rel[:-9] + ".sch" in ALLNAMES:
                continue
            if any(n.endswith("/" + rel) for n in ALLREL):
                continue
            if rel in ALLOWLIST:
                used.add(rel)
                continue
            bad_path.append((base, i, rel))

stale = sorted(set(ALLOWLIST) - used)
print("scanned %d markdown files" % len(files))
print("section refs : %d checked, %d dangling" % (nsec, len(bad_sec)))
for b in bad_sec:
    print("   DANGLING %s:%d  section %s does not exist in %s" % b)
print("path refs    : %d checked, %d allowlisted, %d unresolved"
      % (npath, len(used), len(bad_path)))
for b in bad_path:
    print("   UNRESOLVED %s:%d  %s   <- not on the allowlist" % b)
for r in stale:
    print("   STALE allowlist entry, now resolves or is unreferenced: %s" % r)
ok = not bad_sec and not bad_path and not stale
print("")
print("RESULT: %s" % ("PASS -- every section and path reference resolves" if ok else "FAIL"))
raise SystemExit(0 if ok else 1)
