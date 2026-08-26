# DE.3 in the GF180MCU KLayout DRC deck: three defects, one of them behavioural

**Status:** written 2026-08-25 as a record. **Not filed anywhere.** Found while adding density
keep-out markers (rung 2); it does not affect our design, because the only NDMY we draw is
2,545.9 um2 -- 17% of the cap.

**File:** `gf180mcu/gf180mcuD/libs.tech/klayout/tech/drc/rule_decks/dummy_exclude.drc`
**PDK doc:** the rule text cites
`gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_10_08.html`

## The rule as written

```ruby
# Rule DE.3: Maximum NDMY size (um2) is 15000 um2.
## If size greater than 15000 um2 then two sides should not be greater than (80 um).
logger.info('Executing rule DE.3')
de3_ndmy_area = ndmy.with_area(15_000.um, nil).edges
de3_l1 = de3_ndmy_area.with_length(80.001.um, nil)
de3_l = de3_ndmy_area.join(de3_l1)
de3_l.output('DE.3', 'DE.3 : Maximum NDMY size (um2): 15000 um2.
              If size greater than 15000 um2 then two sides should not be greater than (80 um).')
```

## Defect 1 -- `.join` is a no-op, and it double-reports every violation

`de3_ndmy_area` is the edge collection of every NDMY polygon with area >= 15,000 um2.
`de3_l1` is built by filtering **that same collection**, so `de3_l1` is a subset of
`de3_ndmy_area`. Joining a set with its own subset returns the set:

    de3_l = de3_ndmy_area.join(de3_l1) == de3_ndmy_area

The 80 um criterion therefore cannot change *which* shapes are reported. What it does change is
*how many times* each edge is reported: `join` concatenates rather than merging, so every edge
long enough to also appear in `de3_l1` is emitted **twice**.

**Measured.** A single 100 x 151 um NDMY rectangle (15,100 um2) run through the variant-D deck:

```
DE.3       x8
       edge: (150,0;150,151)
       edge: (150,151;250,151)
       edge: (250,151;250,0)
       edge: (250,0;150,0)
       edge: (150,0;150,151)      <- same four edges again
       edge: (150,151;250,151)
       ...
```

Four edges, eight violations. Any tool or human counting DE.3 violations gets double the real
number for a rectangle (and, in general, inflated by the count of edges >= 80.001 um).

## Defect 2 -- the documented 80 um escape is not implemented, in either direction

The rule *text* describes a conditional: over 15,000 um2 is acceptable provided two sides are
not greater than 80 um. The code implements no such escape -- **every** NDMY polygon at or above
the area threshold is reported, unconditionally.

Nor is there an independent side-length check for shapes *under* the cap. `with_length` is
applied only to edges of already-over-area shapes, so for any shape below 15,000 um2 the filter
is unreachable.

**Measured.** A 182 x 80 um NDMY (14,560 um2, one side 182 um -- more than twice the stated
80 um limit) produces **no DE.3 violation at all**. A 100 x 149 um NDMY (14,900 um2) likewise
passes; a 100 x 151 um (15,100 um2) fails. The rule is a pure area cap with a hard edge at
15,000 um2 and no side-length component whatsoever.

Whichever reading of the DRM is correct, the deck implements neither: it is stricter than the
text for over-area shapes (no escape) and more permissive for under-area ones (no side limit).

## Defect 3 -- `.um` on an area argument (cosmetic, verified harmless)

`with_area` takes an area. The deck passes `15_000.um`, a **linear** unit constructor. Compare
`de3_l1 = ...with_length(80.001.um, nil)`, where `.um` is correct because length is linear.

This one is worth stating precisely: it is a **readability/consistency defect, not a behavioural
one**. The bracketing test above puts the threshold between 14,900 and 15,100 um2, so
`15_000.um` does evaluate to 15,000 um2 as intended. It should still read `15_000` or the
area-typed form, both to match the other area rules in the deck and because the current form
invites exactly the "is this actually 15,000 um2?" doubt that prompted this test.

## Suggested fix

```ruby
de3_l = ndmy.with_area(15_000, nil).edges
de3_l.output('DE.3', '...')
```

That preserves today's *effective* behaviour (area cap only) while dropping the duplicate
reporting and the dead filter. If the DRM's conditional is the intended rule, it needs a real
implementation -- select over-area polygons, then reject only those with two or more sides
> 80 um -- which is a different query, not a filter on the same edge collection.

## Reproduction

```
# four NDMY (111/5) rectangles in one flat cell, spaced 50 um apart:
#   A 100 x 149 = 14,900 um2   B 100 x 151 = 15,100 um2
#   C 182 x  80 = 14,560 um2   D  50 x  50 =  2,500 um2
python3 <pdk>/libs.tech/klayout/tech/drc/run_drc.py --path=de3probe.gds         --variant=D --topcell=de3probe --run_dir=<dir> --run_mode=flat
# result: DE.3 x8, all eight on B. A, C and D clean.
```
