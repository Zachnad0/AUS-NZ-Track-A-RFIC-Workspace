#!/usr/bin/env python3
# route_selftest.py -- build isolated routing primitives and write test_route.gds for DRC.
import pya, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_lib as R

ly = pya.Layout()
ly.dbu = 0.005
cell = ly.create_cell("test_route")

# a full M1->M5 via stack at (10,10)
R.via_stack(cell, ly, 1, 5, 10.0, 10.0)
# an M4 horizontal wire and an M3 vertical wire crossing (different layers, no short)
R.hwire(cell, ly, 4, 5.0, 20.0, 15.0, w=0.6)
R.vwire(cell, ly, 3, 5.0, 20.0, 12.0, w=0.6)
# a wide M2 power strap
R.hwire(cell, ly, 2, 5.0, 25.0, 5.0, w=2.0)
# an M5 wire (min width/area sensitive)
R.hwire(cell, ly, 5, 25.0, 35.0, 20.0, w=0.6)
# connect the M2 strap up to M4 at (22,5)
R.via_stack(cell, ly, 2, 4, 22.0, 5.0)

ly.write("/foss/designs/AUS-NZ-integration/gds/test_route.gds")
print("wrote test_route.gds; cells:", [c.name for c in ly.top_cells()])
