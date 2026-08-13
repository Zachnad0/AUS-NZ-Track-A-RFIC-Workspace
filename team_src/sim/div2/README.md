# DIV2 self-biased converter sims (Phase 3, 2026-08-12)

Netlist-level validation of the reworked CML→CMOS output converter. Results in
`docs/div2-debug.md` (2026-08-12 section). Run in `iic-osic-tools_xvnc` after
`sak-pdk gf180mcuD`.

## Flow
1. Netlist the TB: from `team_src/xschem`,
   `xschem -n -q -o /foss/designs/_div2_work DIV2_QUAD_tb.sch`.
2. `python3 mk_sb.py` rewrites all four converter chains (_IP _IN _QP _QN) of that
   netlist to the self-biased AC-coupled topology and writes `div2_sb.spice`
   (a full 20 ns `tran` deck). Converter knobs are the `P` dict at the top.
3. `ngspice -b div2_sb.spice`; analyze the dumped `sb_quad.dat` with
   `awk -v CORNER=xx -f analyze.awk sb_quad.dat` (swings, freq, duty, I/Q phase).
   Corners: `sed 's/ngspice typical/ngspice ss/'`; temperature: insert `option temp=85`.

`div2_sb_TT.spice` is a shipped reference of the generated TT deck.

## Topology (per phase, replaces the old DC-coupled 3-inverter chain)
diff-pair front end (unchanged: M_NT tail, M_BN1/2 in = OIB/OI, M_BP1/2 mirror load
-> OC) --> **CC (100 fF) AC-couple** --> node G1 --> **self-biased inverter INV1
(pfet 10u / nfet 4u) with RFB (20 kO) INVO1->G1** --> INV2 (26u/11u balanced) -->
INV3 driver (44u/16u, R_SER 1k) --> I_P. The RFB self-bias holds G1=INVO1=Vtrip
automatically; AC coupling removes OC's common-mode. No absolute threshold to match.

## Headline (16-20 ns unless noted)
TT I_P 142 mVpp, 2.500 GHz, duty 48.8%, I/Q 270.0 deg; FF 146 mVpp; SS 130 mVpp.
Settled (24-28 ns) every corner incl 85C = exact 2.500 GHz / 270.0 deg.
Supply 22.4 mA avg << 50 mA. Slow-hot corners settle ~24-26 ns (see debug doc).
