#!/usr/bin/env python3
# mk_div2_golden.py -- GENERATE the DIV2_QUAD_v1 LVS golden from the netlisted .sch
# (rule 12: never hand-type the golden). Reads the xschem netlist, keeps the FETs,
# and maps the ideal R/C onto the real gf180 layout devices:
#   ideal R value -> ppolyf_u_1k (3-term: e1 e2 bulk=VSS), r_width/r_length by value
#   ideal C 100f  -> cap_mim_2f0_m4m5_noshield (2-term), c_width/c_length for 100fF
# Layout geometries (golden r_width/r_length MUST equal what the layout draws). Locked
# run #6: same L/W ratio as the value needs, but LARGER bodies so end/contact resistance
# is a small fraction (matters for the 300ohm CML loads that set the ~703mV swing via
# I*R) and width is >= 2um (w=1 is the gencell min, where poly resistors match worst):
#   1k=w2 l2 | 300=w10 l3 (l/w=0.3) | 20k=w2 l40 (l/w=20) | 100f cap = w5 l10 (50um^2)
import re, sys

NL  = sys.argv[1] if len(sys.argv) > 1 else '/tmp/DIV2_QUAD_v1.spice'
OUT = sys.argv[2] if len(sys.argv) > 2 else \
      '/foss/designs/AUS-NZ-integration/team_src/magic/DIV2_QUAD_v1_golden.spice'
# 20k drawn SERPENTINE nx2 l20.6: magic extracts r_length=40.04u (41.2u drawn leg-sum
# minus the serpentine corner over-count). Under the PDK model (sm141064: rsh=1000/sq,
# r_dw=0.0148u width-narrowing -> r_n=40.04/1.9704=20.32sq, + 2 terminal R ~87ohm) this
# is ~20.4kOhm typ @25C -- ~2% over ideal 20k, negligible vs the +/-20% rsh corner
# (16.3-24.5k) and RFB*CC=2ns/80MHz. r_length MUST equal the drawn geometry (netgen
# checks it); the resistance is verified against the model, not encoded blind.
RES = {'300': (10.0, 3.0), '20k': (2.0, 40.04), '1k': (2.0, 2.0)}   # value -> (w,l) um
CAP = (5.0, 10.0)   # 100f MIM w,l um (50 um^2 @ 2 fF/um^2)
PORTS = "CK CKB IBIAS I_P I_N Q_P Q_N VDD VSS"

# join continuation lines ("+")
raw = open(NL).read().splitlines()
lines, cur = [], ''
for ln in raw:
    if ln.startswith('+'):
        cur += ' ' + ln[1:].strip()
    else:
        if cur: lines.append(cur)
        cur = ln
if cur: lines.append(cur)

out = [f".subckt DIV2_QUAD_v1 {PORTS}"]
nfet = pfet = nres = ncap = 0
for ln in lines:
    t = ln.split()
    if not t: continue
    if t[0].startswith('X') and ('nfet_03v3' in ln or 'pfet_03v3' in ln):
        # X<name> D G S B <model> L=..u W=..u nf=..  (drop parasitic props)
        name, D, G, S, B, model = t[0], t[1], t[2], t[3], t[4], t[5]
        L = re.search(r'\bL=(\S+)', ln).group(1)
        W = re.search(r'\bW=(\S+)', ln).group(1)
        nf = re.search(r'\bnf=(\S+)', ln)
        nf = nf.group(1) if nf else '1'
        out.append(f"{name} {D} {G} {S} {B} {model} L={L} W={W} nf={nf} m=1")
        if model.startswith('nfet'): nfet += 1
        else: pfet += 1
    elif re.match(r'^R\w', t[0]):
        # R<name> A B <value>  -> X<name> A B VSS ppolyf_u_1k r_width r_length
        name, A, B, val = t[0], t[1], t[2], t[3]
        w, l = RES[val]
        out.append(f"X{name} {A} {B} VSS ppolyf_u_1k r_width={w}u r_length={l}u")
        nres += 1
    elif re.match(r'^C\w', t[0]):
        name, A, B, val = t[0], t[1], t[2], t[3]
        w, l = CAP
        out.append(f"X{name} {A} {B} cap_mim_2f0_m4m5_noshield c_width={w}u c_length={l}u")
        ncap += 1
out.append(".ends DIV2_QUAD_v1")
open(OUT, 'w').write('\n'.join(out) + '\n')
print(f"wrote {OUT}: {nfet} nfet + {pfet} pfet + {nres} res + {ncap} cap "
      f"= {nfet+pfet+nres+ncap} devices")
