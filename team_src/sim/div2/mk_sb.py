#!/usr/bin/env python3
# Rewrite ALL FOUR converter chains (_IP _IN _QP _QN) of the DIV2 TB netlist to
# the self-biased AC-coupled topology; 20 ns tran; dump the 4 CMOS outputs.
P = dict(RFB='20k', CC='100f', WP1='10u', WN1='4u', WP2='26u', WN2='11u',
         WP3='44u', WN3='16u')
PH = ['IP','IN','QP','QN']

src = open('/foss/designs/_div2_work/DIV2_QUAD_tb.spice').read().splitlines()
out = []

def ph_of(tok, s):
    # s starts with tok+'_'; return phase suffix (IP/IN/QP/QN) or None
    rest = s.split()[0][len(tok)+1:]
    return rest if rest in PH else None

for ln in src:
    s = ln.strip()
    done = False
    for ph in PH:
        if s.startswith(f'XM_IP1_{ph} '):
            out.append(f"XM_IP1_{ph} INVO1_{ph} G1_{ph} VDD VDD pfet_03v3 L=0.3u W={P['WP1']} nf=1")
            out.append(f"CC_{ph} OC_{ph} G1_{ph} {P['CC']}")
            out.append(f"RFB_{ph} INVO1_{ph} G1_{ph} {P['RFB']}")
            done = True; break
        if s.startswith(f'XM_IN1_{ph} '):
            out.append(f"XM_IN1_{ph} INVO1_{ph} G1_{ph} VSS VSS nfet_03v3 L=0.3u W={P['WN1']} nf=1")
            done = True; break
        if s.startswith(f'XM_IP2_{ph} '):
            out.append(f"XM_IP2_{ph} INVO2_{ph} INVO1_{ph} VDD VDD pfet_03v3 L=0.3u W={P['WP2']} nf=1")
            done = True; break
        if s.startswith(f'XM_IN2_{ph} '):
            out.append(f"XM_IN2_{ph} INVO2_{ph} INVO1_{ph} VSS VSS nfet_03v3 L=0.3u W={P['WN2']} nf=1")
            done = True; break
        if s.startswith(f'XM_IP3_{ph} '):
            out.append(f"XM_IP3_{ph} INVO3_{ph} INVO2_{ph} VDD VDD pfet_03v3 L=0.3u W={P['WP3']} nf=1")
            done = True; break
        if s.startswith(f'XM_IN3_{ph} '):
            out.append(f"XM_IN3_{ph} INVO3_{ph} INVO2_{ph} VSS VSS nfet_03v3 L=0.3u W={P['WN3']} nf=1")
            done = True; break
    if done:
        continue
    # drop the '+' continuation of any replaced device
    if s.startswith('+') and out and (out[-1].split()[0] in
            [f'XM_IP1_{p}' for p in PH]+[f'XM_IN1_{p}' for p in PH]+
            [f'XM_IP2_{p}' for p in PH]+[f'XM_IN2_{p}' for p in PH]+
            [f'XM_IP3_{p}' for p in PH]+[f'XM_IN3_{p}' for p in PH]+
            [f'RFB_{p}' for p in PH]):
        continue
    if s.startswith('.tran') or s == '.end':
        continue
    out.append(ln)

ctrl = """
.save all
.control
tran 0.2p 20n uic
wrdata /foss/designs/_div2_work/sb_quad.dat v(I_P) v(I_N) v(Q_P) v(Q_N) v(x1.INVO3_IP) v(x1.INVO3_QP)
.endc
.end
"""
open('/foss/designs/_div2_work/div2_sb.spice','w').write("\n".join(out) + ctrl)
print("wrote div2_sb.spice (all 4 phases)")
