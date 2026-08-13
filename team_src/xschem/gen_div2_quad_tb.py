#!/usr/bin/env python3
# DIV2_QUAD_v1 testbench: 240u into IBIAS, rail-to-rail differential 5 GHz clock,
# pad load (300fF + 50ohm) on each output. 20 ns tran (measure 16-20 ns settled;
# slow-hot corners settle ~24-26 ns -- see docs/div2-debug.md). Startup .ic seeds
# the CML latch (deterministic division) and pre-charges the converter self-bias
# nodes G1_* (cuts the RFB*CC settling). Output path relative to this script.
import io, os
o=io.StringIO()
def e(s): o.write(s+"\n")
e("v {xschem version=3.4.8RC file_version=1.3}")
for h in ["G {}","K {}","V {}","S {}","F {}","E {}"]: e(h)
lpn=[0]
def lab(x,y,n):
    lpn[0]+=1; e("C {lab_pin.sym} %d %d 0 0 {name=lp%d lab=%s}"%(x,y,lpn[0],n))
pins={"CK":(-150,-60),"CKB":(-150,-20),"IBIAS":(-150,20),
      "I_P":(150,-60),"I_N":(150,-20),"Q_P":(150,20),"Q_N":(150,60),
      "VDD":(0,-100),"0":(0,100)}
ix,iy=0,0
e("C {DIV2_QUAD_v1.sym} %d %d 0 0 {name=X1}"%(ix,iy))
for n,(dx,dy) in pins.items(): lab(ix+dx,iy+dy,n)
e('C {vsource.sym} -600 -300 0 0 {name=V_VDD value="3.3" savecurrent=true}')
lab(-600,-330,"VDD"); lab(-600,-270,"0")
e('C {vsource.sym} -600 0 0 0 {name=V_CK value="PULSE(0 3.3 0 5p 5p 95p 200p)" savecurrent=false}')
lab(-600,-30,"CK"); lab(-600,30,"0")
e('C {vsource.sym} -600 300 0 0 {name=V_CKB value="PULSE(3.3 0 0 5p 5p 95p 200p)" savecurrent=false}')
lab(-600,270,"CKB"); lab(-600,330,"0")
e('C {isource.sym} -900 20 0 0 {name=I_BIAS value=240u}')
lab(-900,-10,"VDD"); lab(-900,50,"IBIAS")
outs=[("I_P",600),("I_N",900),("Q_P",1200),("Q_N",1500)]
for nm,xx in outs:
    e('C {capa.sym} %d 200 0 0 {name=Cpad_%s value=300f}'%(xx,nm)); lab(xx,170,nm); lab(xx,230,"0")
    e('C {res.sym} %d 400 0 0 {name=Rterm_%s value=50 footprint=1206 device=resistor m=1}'%(xx,nm)); lab(xx,370,nm); lab(xx,430,"0")
# startup .ic: seed CML latch (OI/OIB strong, OQ/OQB slight offset to break Q
# metastability) + pre-charge converter self-bias nodes to ~INV1 trip.
ic = ("v(x1.OI)=3.2 v(x1.OIB)=2.5 v(x1.OQ)=2.9 v(x1.OQB)=2.8 "
      "v(x1.G1_IP)=1.5 v(x1.G1_IN)=1.5 v(x1.G1_QP)=1.5 v(x1.G1_QN)=1.5")
e('C {code_shown.sym} -900 700 0 0 {name=s1 only_toplevel=false value="')
e('.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice')
e('.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical')
e('.save all i(V_VDD)')
e('.ic '+ic)
e('.tran 0.2p 20n uic')
e('"}')
dst=os.path.join(os.path.dirname(os.path.abspath(__file__)),"DIV2_QUAD_tb.sch")
open(dst,"w").write(o.getvalue())
print("wrote",dst)
