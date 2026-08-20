#!/usr/bin/env bash
# verify_cp.sh <CELL>
#
# DRC + LVS a cell layout against its golden netlist, headless.
#   layout : gds/<CELL>.gds  (preferred, the committed tapeout artifact)
#            else team_src/magic/<CELL>.mag
#   golden : team_src/magic/<CELL>_golden.spice
#
# Prints DRC error count, extracted functional device/port/net counts, and the
# netgen verdict. Exits non-zero if DRC > 0 or LVS is not a unique match.
#
# Paths to the magicrc and netgen setup are taken from the live PDK env
# ($PDK_ROOT/$PDK); the script hard-fails with a hint if either is missing
# rather than silently passing.
set -u

CELL="${1:-}"
if [ -z "$CELL" ]; then
    echo "usage: verify_cp.sh <CELL>" >&2
    exit 2
fi

fail() { echo "verify_cp: FATAL: $*" >&2; exit 3; }

# --- locate ourselves and the repo ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # team_src/magic
MAGIC_DIR="$SCRIPT_DIR"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORK="$MAGIC_DIR/verify_work"
mkdir -p "$WORK"

# --- PDK env (source the sak setup if the tools/env are not already present) ---
: "${PDK:=gf180mcuD}"
if ! command -v magic >/dev/null 2>&1 || [ -z "${PDK_ROOT:-}" ]; then
    # shellcheck disable=SC1091
    source /foss/tools/sak/sak-pdk-script.sh "$PDK" >/dev/null 2>&1 || true
fi
: "${PDK_ROOT:=/foss/pdks}"

MAGICRC="$PDK_ROOT/$PDK/libs.tech/magic/$PDK.magicrc"
NETGEN_SETUP="$PDK_ROOT/$PDK/libs.tech/netgen/${PDK}_setup.tcl"
STD_SPICE="$PDK_ROOT/$PDK/libs.ref/gf180mcu_fd_sc_mcu7t5v0/spice/gf180mcu_fd_sc_mcu7t5v0.spice"

command -v magic  >/dev/null 2>&1 || fail "magic not on PATH (source /foss/tools/sak/sak-pdk-script.sh $PDK)"
command -v netgen >/dev/null 2>&1 || fail "netgen not on PATH (source /foss/tools/sak/sak-pdk-script.sh $PDK)"
[ -f "$MAGICRC" ]      || fail "magicrc not found: $MAGICRC  (is PDK=$PDK correct under $PDK_ROOT?)"
[ -f "$NETGEN_SETUP" ] || fail "netgen setup not found: $NETGEN_SETUP  (check $PDK_ROOT/$PDK/libs.tech/netgen)"
[ -f "$SCRIPT_DIR/verify_extract.tcl" ] || fail "missing companion verify_extract.tcl next to this script"

GOLDEN="$MAGIC_DIR/${CELL}_golden.spice"
[ -f "$GOLDEN" ] || fail "golden netlist not found: $GOLDEN"

# --- layout source: committed GDS preferred, else magic .mag ---
if   [ -f "$REPO_ROOT/gds/$CELL.gds" ]; then SRC="$REPO_ROOT/gds/$CELL.gds"; SRCTYPE="gds"
elif [ -f "$MAGIC_DIR/$CELL.mag" ];     then SRC="$MAGIC_DIR/$CELL.mag";     SRCTYPE="mag"
else fail "no layout source: neither gds/$CELL.gds nor team_src/magic/$CELL.mag exists"
fi

LVS_SPICE="$WORK/$CELL.lvs.spice"
DRC_LOG="$WORK/$CELL.drc.log"
LVS_LOG="$WORK/$CELL.lvs.log"
COMP_OUT="$WORK/$CELL.comp.out"
GOLD_RES="$WORK/$CELL.golden_resolved.spice"
LOCAL_SETUP="$WORK/${CELL}.netgen_setup_local.tcl"

echo "== verify_cp: $CELL =="
echo "   layout : $SRC ($SRCTYPE)"
echo "   golden : $GOLDEN"

# --- optional per-cell ABSTRACT config: <CELL>.abstract lines PRELOAD=/PRELOAD_PATH=/IGNORE=
#     For cells that instance a magic abstract (LEFview + GDS_FILE, e.g. the VCO spiral):
#     preload the abstract so the GDS extract keeps it, and black-box it in netgen.
#     No file -> no effect (regression-safe for CP_v1, ibias_gen_v1, DIV2_QUAD_v1, ...). ---
ABS_CFG="$MAGIC_DIR/${CELL}.abstract"
VPRELOAD=""; VPRELOAD_PATH=""; VIGNORE=""
if [ -f "$ABS_CFG" ]; then
    VPRELOAD="$(sed -n 's/^PRELOAD=//p' "$ABS_CFG" | tr '\n' ' ')"
    VPRELOAD_PATH="$(sed -n 's/^PRELOAD_PATH=//p' "$ABS_CFG" | head -1)"
    VIGNORE="$(sed -n 's/^IGNORE=//p' "$ABS_CFG" | tr '\n' ' ')"
    echo "   abstract: preload [$VPRELOAD] ignore [$VIGNORE]"
fi

# --- Magic: DRC + LVS-netlist extraction ---
rm -f "$LVS_SPICE"
( cd "$WORK" && \
  VERIFY_CELL="$CELL" VERIFY_SRC="$SRC" VERIFY_SRCTYPE="$SRCTYPE" VERIFY_OUT="$LVS_SPICE" \
  VERIFY_PRELOAD="$VPRELOAD" VERIFY_PRELOAD_PATH="$VPRELOAD_PATH" \
  magic -dnull -noconsole -rcfile "$MAGICRC" "$SCRIPT_DIR/verify_extract.tcl" ) > "$DRC_LOG" 2>&1

DRC="$(grep -oE 'VERIFY_DRC_COUNT=[0-9]+' "$DRC_LOG" | tail -1 | cut -d= -f2)"
[ -f "$LVS_SPICE" ] || fail "extraction produced no netlist; see $DRC_LOG"
[ -n "${DRC:-}" ]   || fail "could not parse DRC count from magic; see $DRC_LOG"

# --- functional device / port / net counts from the extracted top subckt ---
# (exclude placer-inserted fill / decap / endcap / filltie -- not LVS devices)
read -r DEV FILL PORTS NETS < <(awk -v c="$CELL" '
    BEGIN{IGNORECASE=1}
    $1==".subckt" && $2==c {intop=1; ports=NF-2; next}
    intop && $1==".ends" {intop=0}
    intop && /^X/ {
        if ($0 ~ /fillcap_|__fill_[0-9]|__endcap|__filltie/) { fill++; next }
        dev++
        for (i=2;i<=NF;i++){ if ($i !~ /=/ && $i !~ /^gf180mcu/) nets[$i]=1 }
    }
    END{ n=0; for (k in nets) n++; printf "%d %d %d %d\n", dev, fill, ports, n }
' "$LVS_SPICE")

# --- resolve golden std-cell instances against the PDK spice so both circuits
#     carry full definitions (digital blocks); harmless for transistor-level goldens ---
: > "$GOLD_RES"
if grep -q "gf180mcu_fd_sc_mcu7t5v0__" "$GOLDEN"; then
    [ -f "$STD_SPICE" ] || fail "golden uses mcu7t5v0 std cells but PDK std-cell spice is missing: $STD_SPICE"
    printf '.include %s\n' "$STD_SPICE" >> "$GOLD_RES"
fi
printf '.include %s\n' "$GOLDEN" >> "$GOLD_RES"

# --- local netgen setup: stock PDK setup + enable the (PDK-provided, commented)
#     fillcap-decap ignore, so a placed layout LVSes against a schematic golden ---
{
    printf 'source %s\n' "$NETGEN_SETUP"
    printf 'foreach cell $cells1 { if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} { ignore class "-circuit1 $cell" } }\n'
    printf 'foreach cell $cells2 { if {[regexp {gf180mcu_fd_sc_[^_]+__fillcap_[[:digit:]]+} $cell match]} { ignore class "-circuit2 $cell" } }\n'
    for ig in $VIGNORE; do
        printf 'ignore class "-circuit1 %s"\n' "$ig"
        printf 'ignore class "-circuit2 %s"\n' "$ig"
    done
} > "$LOCAL_SETUP"

# --- netgen LVS ---
netgen -batch lvs "$LVS_SPICE $CELL" "$GOLD_RES $CELL" "$LOCAL_SETUP" "$COMP_OUT" > "$LVS_LOG" 2>&1

# Property errors: netgen still declares "Circuits match uniquely" when device
# W/L differ beyond its 1% cutoff -- it reports them separately as property
# errors (Phase 1 finding, gf180 nfet/pfet_03v3 are pin-only black boxes so
# topology can match uniquely while sizes are wrong). A wrongly-sized layout
# must NOT pass, so treat any property error as a hard LVS failure.
if grep -qiE "property error|with property errors" "$COMP_OUT"; then PROP_ERR=1; else PROP_ERR=0; fi

if   grep -q "Circuits match uniquely" "$COMP_OUT" && [ "$PROP_ERR" -eq 0 ]; then
    VERDICT="match uniquely"; LVS_OK=1
elif grep -q "Circuits match uniquely" "$COMP_OUT" && [ "$PROP_ERR" -eq 1 ]; then
    VERDICT="topology matches uniquely BUT device property errors (W/L mismatch)"; LVS_OK=0
elif grep -q "Circuits match with" "$COMP_OUT"; then VERDICT="$(grep -m1 'Circuits match with' "$COMP_OUT")"; LVS_OK=0
elif grep -qi "do not match" "$COMP_OUT";           then VERDICT="DO NOT MATCH"; LVS_OK=0
else VERDICT="INDETERMINATE (see $COMP_OUT)"; LVS_OK=0
fi

echo "---- results ----"
echo "DRC errors        : ${DRC}"
echo "devices (LVS)     : ${DEV}    (+${FILL} fill/decap ignored)"
echo "ports             : ${PORTS}"
echo "nets              : ${NETS}"
echo "LVS verdict       : ${VERDICT}"
if [ "$PROP_ERR" -eq 1 ]; then
    echo "property errors   :"
    # print netgen's per-device W/L delta lines (device-vs-device + delta=/cutoff=)
    grep -E 'vs\.|delta=|cutoff=' "$COMP_OUT" | sed 's/^/   /' | head -20
fi
echo "logs              : $DRC_LOG | $COMP_OUT"

RC=0
if [ "${DRC}" -ne 0 ]; then echo "GATE FAIL: DRC = ${DRC} (> 0)"; RC=1; fi
if [ "${LVS_OK}" -ne 1 ]; then echo "GATE FAIL: LVS not a clean unique match"; RC=1; fi
if [ "$RC" -eq 0 ]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
exit "$RC"
