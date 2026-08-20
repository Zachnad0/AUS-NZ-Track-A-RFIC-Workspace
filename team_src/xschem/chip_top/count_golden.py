import sys
D="/foss/designs/AUS-NZ-integration/team_src/magic"
BLOCKS=["PFD_lib","CP_v1","ibias_gen_v1","DIV2_QUAD_v1","vco_v1"]
def counts(path, subckt):
    dev=dict(M=0,X=0,R=0,C=0,L=0); inblk=(subckt is None); ports={}
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("*"): continue
        low=s.lower()
        if low.startswith(".subckt"):
            parts=s.split(); ports[parts[1]]=parts[2:]
            if subckt and parts[1]==subckt: inblk=True
            continue
        if low.startswith(".ends"):
            if subckt: inblk=False
            continue
        if inblk and s[0].upper() in dev: dev[s[0].upper()]+=1
    return dev,ports
print("=== per-block golden device counts ===")
tot=dict(M=0,X=0,R=0,C=0,L=0)
for b in BLOCKS:
    d,p=counts("%s/%s_golden.spice"%(D,b),b)
    print("  %-14s M=%d X=%d R=%d C=%d L=%d  ports=%d %s"%(b,d["M"],d["X"],d["R"],d["C"],d["L"],len(p[b]),p[b]))
    for k in tot: tot[k]+=d[k]
print("  %-14s M=%d X=%d R=%d C=%d L=%d"%("SUM",tot["M"],tot["X"],tot["R"],tot["C"],tot["L"]))
print("=== chip_top_golden.spice ===")
dc,pc=counts("%s/chip_top_golden.spice"%D,None)
print("  raw   M=%d X=%d R=%d C=%d L=%d"%(dc["M"],dc["X"],dc["R"],dc["C"],dc["L"]))
print("  X minus 5 chip-top block instances = %d"%(dc["X"]-5))
print("  chip_top ports (%d):"%len(pc.get("chip_top",[])), pc.get("chip_top"))
print("  subckts defined:", sorted(pc.keys()))
